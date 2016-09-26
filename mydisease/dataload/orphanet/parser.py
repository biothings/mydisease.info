import xml.etree.ElementTree as et
from collections import defaultdict

import pandas as pd
from mydisease.utils.common import list2dict
from pymongo import MongoClient

from . import ages_path, gene_path, hpo_path, ordo_path, prev_path, xref_path


def parse_ordo():
    columns_rename = {"http://data.bioontology.org/metadata/obo/part_of": "part_of",
                      "http://data.bioontology.org/metadata/treeView": "tree_view",
                      "http://www.ebi.ac.uk/efo/alternative_term": "alternative_term",
                      "http://www.ebi.ac.uk/efo/definition": "definition",
                      "http://www.ebi.ac.uk/efo/definition_citation": "definition_citation",
                      "http://www.ebi.ac.uk/efo/reason_for_obsolescence": "reason_for_obsolescence",
                      "http://www.geneontology.org/formats/oboInOwl#hasDbXref": "xref",
                      "http://www.orpha.net/ORDO/Orphanet_#symbol": "symbol",
                      "Synonyms": "synonyms",
                      "Obsolete": "obsolete",
                      "Class ID": "id",
                      "Preferred Label": "preferred_label",
                      "Parents": "parents",
                      "Definitions": "definitions"
                      }
    df = pd.read_csv(ordo_path)
    del df["http://www.geneontology.org/formats/oboInOwl#hasDbXref"]
    # throw away columns that are all null
    df = df[df.columns[df.isnull().sum() != len(df)]]
    df = df.rename(index=str, columns=columns_rename)
    df = df[~df.obsolete]
    df = df[df.symbol.isnull()]
    del df['obsolete']

    for col in ['parents', 'part_of', 'tree_view', 'id']:
        df[col] = df[col].str.replace("http://www.orpha.net/ORDO/", "").str.replace("_", ":").str.lower()
    list_attribs = ['synonyms', 'parents', 'part_of', 'tree_view', 'alternative_term']
    for col in list_attribs:
        df[col] = df[col].str.split("|").copy()
    df.rename(columns={'id': '_id'}, inplace=True)

    df_records = df.apply(lambda x: x.dropna().to_dict(), axis=1)
    d = {record["_id"]: record for record in df_records}
    return d


def parse_xref(d):
    # # Load in cross refs
    # ## Rare diseases and cross-referencing
    # ## Keeping xref as those with exact match (E) or BTNT (broad term -> narrow term)
    # modifies d in place
    import xml.etree.ElementTree as et
    tree = et.parse(xref_path)
    root = tree.getroot()

    id_replace = {"umls": "umls_cui",
                  "icd-10": "icd10cm"}
    for disease in root.find("DisorderList"):
        name = disease.find("Name").text
        orpha = "orphanet:" + disease.find("OrphaNumber").text
        references = disease.findall("ExternalReferenceList/ExternalReference")
        mapping = defaultdict(list)
        xrefs = []
        for ref in references:
            source = ref.find("Source").text.lower()
            source = id_replace.get(source, source)
            reference = ref.find("Reference").text
            mapping_relation = ref.find("DisorderMappingRelation/Name").text.split(" ", 1)[0]
            if source == "icd10cm":
                reference = reference.replace("-", "").replace("*", "").replace("+", "")
            xref = source + ":" + reference
            mapping[mapping_relation].append(xref)
            if mapping_relation in {'E', 'BTNT'}:
                xrefs.append(xref)
        xrefs = list2dict(xrefs)
        synonyms = [x.text for x in disease.findall("SynonymList/Synonym")]
        if orpha in d:
            d[orpha].update({'xref': xrefs, 'mapping': dict(mapping)})
        else:
            d[orpha] = {'preferred_label': name, 'synonyms': synonyms,
                        'xref': xrefs, 'mapping': dict(mapping), '_id': orpha}


def parse_prev():
    """
    # Point prevalence, prevalence at birth, lifetime prevalence, annual incidence, number of cases an/or families
    http://www.orphadata.org/data/xml/en_product2_prev.xml
    http://www.orphadata.org/cgi-bin/docs/userguide2014.pdf

    DisorderType: can be either Disease, Clinical syndrome, Malformation syndrome,
    Biological anomaly, Morphological anomaly, Group of phenomes, Etiological subtype,
    Clinical subtype, Histopathological subtype or Particular clinical situation in a disease
    or syndrome

    PrevalenceList count: total number of epidemiological data of a given entry.

    PrevalenceType: can be either “Point prevalence”, “birth prevalence”, “lifelong
    prevalence”, “incidence”, “cases/families”.

    PrevalenceQualification: can be either “Value and Class”, “Only class”, “Case” or “Family”

    PrevalenceClass: estimated prevalence of a given entry. There are eight possible values:
    \>1 / 1,000, 1-5 / 10,000, 6-9 / 10,000, 1-9 / 100,000, 1-9 / 1,000,000 or <1 / 1,000,000, Not yet documented, Unknown

    ValMoy: Mean value of a given prevalence type. By default, the mean value is 0.0 when only a class is documented.

    PrevalenceGeographic: Geographic area of a given prevalence type

    Source: Source of information of a given prevalence type.

    PrevalenceValidationStatus: can be either Validated or Not yet validated
    """
    tree = et.parse(prev_path)
    root = tree.getroot()
    d = defaultdict(lambda: defaultdict(list))
    for disease in root.find("DisorderList"):
        name = disease.find("Name").text
        orpha = "orphanet:" + disease.find("OrphaNumber").text
        disease_type = disease.find("DisorderType/Name").text
        prevalences = disease.findall("PrevalenceList/Prevalence")
        for prev in prevalences:
            source = prev.find("Source").text
            prevalence_type = prev.find("PrevalenceType/Name").text
            prevalence_qual = prev.find("PrevalenceQualification/Name").text
            prevalence_geo = prev.find("PrevalenceGeographic/Name").text
            prevalence_val_status = prev.find("PrevalenceValidationStatus/Name").text
            valmoy = prev.find("ValMoy").text
            prev_d = {'source': source, 'prevalence_type': prevalence_type, 'prevalence_qualification': prevalence_qual,
                      'prevalence_geographic': prevalence_geo, 'prevalence_validation_status': prevalence_val_status,
                      'mean_value': float(valmoy) if valmoy != '0.0' else None}

            if prev.find("PrevalenceClass/Name") is not None:
                prev_d['prevalence_class'] = prev.find("PrevalenceClass/Name").text
            d[orpha]['prevalence'].append(prev_d)
    return d


def parse_ages(d):
    """
    ## Type of inheritance, average age of onset and average age of death
    http://www.orphadata.org/data/xml/en_product2_ages.xml

    AverageAgeOfOnset: classes based on the estimated average age of entry onset.
    There are ten different population age groups: Antenatal, Neonatal, Infancy,
    Childhood, Adolescence, Adult, Elderly, All ages and No data available.

    AverageAgeOfDeath: classes based on the estimated average age at death for a
    given entry. There are twelve different population age groups: Embryofoetal, Stillbirth,
    Infantile, Early Childhood, Late Childhood, Adolescent,Young adult, Adult, Elderly,
    Any age, Normal life expectancy and No data available.

    TypeOfInheritance: type(s) of inheritance associated with a given disease. There are
    thirteen different types of inheritance: Autosomal dominant, Autosomal recessive, Xlinked
    dominant, X-linked recessive, Chromosomal, Mitochondrial inheritance,
    Multigenic/multifactorial, Oligogenic, Semi-dominant, Y-linked, No data available, Not
    applicable, Not yet documented.
    """

    tree = et.parse(ages_path)
    root = tree.getroot()

    for disease in root.find("DisorderList"):
        orpha = "orphanet:" + disease.find("OrphaNumber").text
        aoo = [x.find("Name").text for x in disease.findall("AverageAgeOfOnsetList/AverageAgeOfOnset")]
        aod = [x.find("Name").text for x in disease.findall("AverageAgeOfDeathList/AverageAgeOfDeath")]
        toi = [x.find("Name").text for x in disease.findall("TypeOfInheritanceList/TypeOfInheritance")]
        ages_d = {'ave_age_of_onset': aoo, 'ave_age_of_death': aod, 'type_of_inheritance': toi}
        ages_d = {k: v for k, v in ages_d.items() if v}
        d[orpha].update(ages_d)


def parse_hpo(d):
    """
    ## Phenotypes associated with rare disorders
    http://www.orphadata.org/cgi-bin/inc/product4.inc.php
    http://www.orphadata.org/data/xml/en_product4_HPO.xml

    Frequencies:
    - Obligate: the phenotype is always present and the diagnosis could not be achieved in its absence;
    - Very frequent: the phenotype is present in 80 to 99% of the patient population ;
    - Frequent: the phenotype is present in 30 to 79% of the patient population ;
    - Occasional: the phenotype is present in 5 to 29% of the patient population ;
    - Very rare: the phenotype is present in 1 to 4% of the patient population ;
    - Excluded: the phenotype is always absent AND is an exclusion criteria for diagnosing the disorder.

    Diagnostic criterion: A diagnostic criterion is a phenotypic abnormality used consensually to
    assess the diagnosis of a disorder. Multiple sets of diagnostic criteria are necessary to
    achieve the diagnosis. Orphanet indicates only diagnostic criteria that are consensually
    accepted by the experts of the medical domain AND published in medical literature.
    Depending of the medical consensus, they could be further qualified as minor, major,
    etc…This level of precision is yet not informed in the Orphanet dataset.

    Pathognomonic sign: A pathognomonic phenotype is a feature sufficient by itself to establish
    definitively and beyond any doubt the diagnosis of the disease concerned (i.e. heliotrope
    erytheme for dermatomyosistis).

    <HPODisorderAssociation id="10225">
      <HPO id="166">
        <HPOId>HP:0001945</HPOId>
        <HPOTerm>Fever</HPOTerm>
      </HPO>
      <HPOFrequency id="28419">
        <OrphaNumber>453312</OrphaNumber>
        <Name lang="en">Frequent (79-30%)</Name>
      </HPOFrequency>
      <DiagnosticCriteria id="28447">
        <OrphaNumber>453316</OrphaNumber>
        <Name lang="en">Pathognomonic sign</Name>
      </DiagnosticCriteria>
    </HPODisorderAssociation>
    """
    tree = et.parse(hpo_path)
    root = tree.getroot()
    for disease in root.find("DisorderList"):
        orpha = "orphanet:" + disease.find("OrphaNumber").text
        associations = disease.findall("HPODisorderAssociationList/HPODisorderAssociation")
        for ass in associations:
            hpo_id = ass.find("HPO/HPOId").text
            hpo_name = ass.find("HPO/HPOTerm").text
            frequency = ass.find("HPOFrequency/Name").text
            pheno_d = {'phenotype_id': hpo_id.lower(), 'phenotype_name': hpo_name,
                       'frequency': frequency}
            if ass.find("DiagnosticCriteria/Name") is not None:
                pheno_d['diagnostic_criteria'] = ass.find("DiagnosticCriteria/Name").text
            d[orpha]['phenotypes'].append(pheno_d)


def parse_gene(d):
    """
    DisorderList count: total number of disorders, group of disorders and subtypes in the XML file.

    Orphanum: unique identifying number assigned by Orphanet to a given entry (disorder, group of disorders, subtype or gene).

    Name: preferred name of a given entry (disorder, group of disorders, subtype or gene).

    GeneList count: number of genes associated with a given entry.

    Symbol: official HGNC-approved gene symbol.

    Synonym list: list of synonyms for a given gene, including past symbols

    GeneType: can be either gene with protein product, locus or non-coding RNA

    GeneLocus: gene chromosomal location

    DisorderGeneAssociationType: gene-disease relationships. They can be either Role in the phenotype of, Disease-causing germline mutation(s) (loss of function) in, Disease-causing germline mutation(s) (gain of function) in, Disease-causing somatic mutation(s) in, Modifying somatic mutation in, Part of a fusion gene in, Major susceptibility factor in and Candidate gene tested in.

    DisorderGeneAssociationStatus: can be either Validated or Not validated

    External Reference List: list of references in HGNC, OMIM, GenAtlas and UniProtKB, Ensembl, Reactome and IU-PHAR associated with a given gene.

    Source: HGNC, OMIM, GenAtlas or UniProtKB.

    Reference: listed reference for a given source associated with a gene
    """
    tree = et.parse(gene_path)
    root = tree.getroot()
    gene_d = {}
    dga_d = defaultdict(list)
    for disease in root.find("DisorderList"):
        orpha = "orphanet:" + disease.find("OrphaNumber").text
        genes = disease.findall("GeneList/Gene")
        for gene in genes:
            synonyms = [x.text for x in gene.findall("SynonymList/Synonym")]
            gene_type = gene.find("GeneType/Name").text
            loci = [x.find("GeneLocus").text for x in gene.findall("LocusList/Locus")]
            gene_d[gene.attrib['id']] = {'synonyms': synonyms, 'gene_type': gene_type,
                                         'loci': loci}
        dg_associations = disease.findall("DisorderGeneAssociationList/DisorderGeneAssociation")
        for dga in dg_associations:
            gene = dga.find("Gene")
            gene_name = gene.find("Name").text
            gene_symbol = gene.find("Symbol").text
            dga_type = dga.find("DisorderGeneAssociationType/Name").text
            dga_status = dga.find("DisorderGeneAssociationStatus/Name").text
            this_dga = {'gene_name': gene_name, 'gene_symbol': gene_symbol,
                        'dga_type': dga_type, 'dga_status': dga_status}
            this_dga['gene_type'] = gene_d[gene.attrib['id']]['gene_type']
            this_dga['loci'] = gene_d[gene.attrib['id']]['loci']
            dga_d[orpha].append(this_dga)
            d[orpha]['disease_gene_associations'].append(this_dga)


def parse(mongo_collection=None, drop=True):
    if mongo_collection:
        db = mongo_collection
    else:
        client = MongoClient()
        db = client.mydisease.orphanet
    if drop:
        db.drop()
    d = parse_ordo()
    parse_xref(d)
    db.insert_many(list(d.values()))

    d = parse_prev()
    parse_ages(d)
    parse_hpo(d)
    parse_gene(d)

    d = {k: dict(v) for k, v in d.items()}
    for k, v in d.items():
        v['_id'] = k
    dlist = list(d.values())

    for dd in dlist:
        db.update_one({'_id': dd['_id']}, {'$set': dd}, upsert=True)
