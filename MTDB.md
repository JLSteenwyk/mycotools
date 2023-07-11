![MycotoolsDB](https://github.com/xonq/mycotools/blob/master/misc/mtdb.png)

# Mycotools Database (MTDB)

MTDBs are locally assimilated, uniformly curated databases of JGI MycoCosm (preferred) and NCBI
fungal or prokaryotic genomic data. MTDBs are represented in tab delimitted database `.mtdb` reference files,
which serve as the scaleable input to Mycotools scripts. 

Herein are the objectives, standards, and expectations of MTDB and associated files.

<br /><br />

## OBJECTIVE

Enable broadscale comparative genomics via a systematically curated, automatically
assembled/updated, scaleable genomics database. MTDB primarily seeks to resolve
several outstanding problems in comparative genomics: 

1. Uniformly curate genomic data within and across multiple databases, i.e. the 
inconsistency of the gene coordinates, `gff` file
2. Promote ease-of-use for scalable and large scale analyses, e.g. transitioning between datasets
in a phylogenetic analysis
3. Keep-up with the accelerating deposition of public genomic data via automatic updates
4. Implement a modular comparative genomic analyses toolkit to enable automated pipelining and 
make routine comparative genomic analyses accessible

<br /><br /><br />

## MTDB standards
### `.mtdb` file format standard
Because MTDBs are essentially tab-delimitted spreadsheets, the database can be
scaled by extracting rows of interest using
`bash`/[extractDB.py](https://gitlab.com/xonq/mycotools/-/blob/primary/mycotools/USAGE.md#creating-modular-databases)
and feeding the scaled MTDB into [Mycotools scripts](https://gitlab.com/xonq/mycotools/-/blob/primary/mycotools/USAGE.md). Master MTDB files are
labelled `YYYYmmdd.mtdb` based on the date the update began; the most recent
`mtdb` in the primary MTDB folder will be used as the primary database.

Example row:
```
#ome    genus   species strain  taxonomy        version source  biosample   assembly_acc    acquisition_date        published       fna     faa     gff3
aaoarx1 Aaosphaeria     arxii   CBS17579        {"clade": "dothideomyceta", "kingdom": "Fungi", "phylum": "Ascomycota", "subphylum": "Pezizomycotina", "class": "Dothideomycetes", "subclass": "Pleosporomycetidae", "order": "Pleosporales", "family": "", "subfamily": "", "genus": "Aaosphaeria", "species": "Aaosphaeria arxii"}    v1.0    jgi             Aaoar1  20210414 Haridas S et al.,2020
```

Tab-delimited file, with one row per genome and ordered columns:
- `ome`: MTDB accession "ome" - first three letters of genus, first three letters of species
(or "sp."), unique database number, and optional MTDB version tag '.\d+', e.g.
`psicub1`/`cryneo24.1` `[a-zA-Z0-9\.]`
- `genus`: Genus name; `[a-zA-Z]`
- `species`: Species name; `[a-zA-Z]`
- `strain`: Strain name; `[a-zA-Z0-9]`
- `taxonomy`: NCBI taxonomy `JSON` object derived from genus
- `version`: MycoCosm version/NCBI modification date
- `source`: Genome source, e.g. 'ncbi'/'jgi'/'lab'; `[a-z0-9\.]`
- `biosample`: optional NCBI BioSample accession
- `assembly_acc`: NCBI GenBank/RefSeq assembly accession or MycoCosm portal
- `published`: Publication metadata or binary publication response; 0/None/''
  are use-restricted - all others are presumed to be open access by Mycotools scripts ([see
  below](https://gitlab.com/xonq/mycotools/-/blob/primary/mycotools/MTDB.md#data-assimilation))
- `acquisition_date`: Date of input into primary database; `YYYYmmdd`
- `fna`: assembly `.fna`, required when not `$MYCOFNA/fna/<ome>.fna`; PATH
- `faa`: proteome `.faa`, required when not `$MYCOFAA/faa/<ome>.faa`; PATH
- `gff3`: gene coordinate `.gff3`, required when not
  `$MYCOGFF3/gff3/<ome>.gff3`; PATH

If headers are included, the line must begin with '#'; generally, lines
beginning with '#' are ignored.

MTDB requires an assembly and gene coordinates `gff3` for ALL GENOMES.
Proteomes will be generated by referencing the assembly and `gff3`.

<br /><br />

### accession formatting
All MTDB aliases will be formatted as `<ome>_<acc>` where `ome` is `ome` in the
MTDB and acc is the retrieved accession for both assemblies and proteomes.
Thus, MTDB aliases are directly connected to the MTDB by slicing to the
underscore.
For JGI, MTDB accessions will pull from the `protein_id` field in the gene coordinates file.
For NCBI, MTDB accessions will pull from the `product_id` field in the gene coordinates file.
For entries without a detected protein ID, an alias will be assigned with the
prefix, 'mtdb'. Pseudogenes, tRNAs, and rRNAs aliases will format as
`<ome>_<type><type_count>`

<br /><br />

### `gff3` gene coordinates file standard
MTDB attempts to curate, assimilate, and modernize ALL MycoCosm and NCBI
annotations, including legacy data. All proteins, associated transcripts, 
exons, gene, and CDSs will include `;Alias=<ome>_<acc>` in the attributes
column. 
All attribute fields will contain `ID=[^;]+`, `Alias=[^;]+`; 
Non-gene entries will have a parent field `Parent=[^;]+` that relates the entry
to its parent RNA and each RNA to their parent gene.

On the occassion GFF entries are not given an Alias, *assume that these are
ignored by Mycotools*; while curation is fairly robust for JGI and NCBI GFFs,
other GFFs may have cryptic formatting discrepancies. CDSs without an alias will 
not be translated into the proteome `faa` fasta.

#### - permitted `gff3` sequence type fields: 
- gene, pseudogene: contains the terminal ID of descendant entries and alias (Alias=.*;) that contains
  all MTDB aliases derived from the gene, separated by `|`. `ID=gene_<ACC>`
- mRNA, tRNA, rRNA, RNA: `RNA` is synonymous with `transcript` and represents
  transcribed, but not translated, sequences without tRNA/rRNA functionality. `ID=<RNA>_<ACC>`
- exon: parent will be an RNA ID; introns will be curated to exons. `ID=exon_<ACC>_<EXON#>`
- CDS: CDS ID parent will be an RNA ID; typically contains a
  `protein_id/product_id` field. `ID=CDS_<ACC>_<CDS#>`

#### - `gff3` attributes field formatting
MTDB recognizes several attribute fields, separated by a semi-colon and
optionally contained within single/double quotes. MTDB permits non-recognized
fields.

- `Alias=<ome>_<acc>`: MTDB accession; REQUIRED
- `ID=[^;]+`: entry `ID`; REQUIRED
- `Parent=[^;]+`: the `ID` this row is descended from, i.e.
  gene->mRNA->CDS/exon
- `[protein_id[^;]+|proteinId=[^;]+]`: protein ID field
- `product=[^;]+`: functional annotation
- `[transcriptId=[^;]+|transcript_id=[^;]+]`: transcript ID field

#### - alternate splicing
Alternately spliced genes are accounted for in curation. Genes with alternately
spliced descendants will have multiple aliases, separated by '|'. mRNAs and
their children will all have unique aliases.

#### - proteome `faa`
Proteomes will be generated on the fly when updating the database by
referencing an MTDB-curated `gff3` and assembly. Proteins are generated from
CDS coordinates that can be tied to an mRNA with a gene parent. 

<br /><br />

### data assimilation
#### - JGI
`mtdb update` will prioritize MycoCosm (JGI) genomes over NCBI by referencing
the submitter field in NCBI assembly metadata. Each unique Portal is retrieved from the
MycoCosm primary table. 

##### JGI use restriction
Use restriction metadata is applied from the associated field in the MycoCosm primary table.
IT IS USER RESPONSIBILITY TO VERIFY THE VALIDITY OF AUTOMATICALLY APPLIED USE-RESTRICTION LABELS.
Please review [JGI policy on use-restricted data](https://jgi.doe.gov/user-programs/pmo-overview/policies/).

#### - NCBI
NCBI genomes will be retrieved from the primary eukaryotes.txt/prokaryotes.txt 
and each unique assembly accession that was not submitted by JGI is retrieved. 
Version checking operates on the `Modify Date` field.

##### taxonomy
All taxonomy metadata is acquired by querying the NCBI taxonomy with the genus
name. Therefore, taxonomy is subject to errors in NCBI taxonomy.

##### NCBI use restriction
All NCBI entries are
assumed to be "published" for non-restricted use. "However, some submitters may claim patent, copyright, or other intellectual property rights in all or a portion of the data they have submitted." - [NCBI](ncbi.nlm.nih.gov/genbank/). It is the user responsbility to determine which, if any, genome data have use-restriction policies.

*There may be edge-case examples
of use-restricted NCBI data, however NCBI cannot provide oversight for their
particular restrictions, and thus MTDB cannot assimilate these data.* A git
issue can be raised for isolated examples, which can then be incorporated into
a manually curated exceptions file; for local handling, simply empty the
publication field for the associated row. MTDBs are user-assimilated databases,
and Mycotools makes no guarantee that it comprehensively addresses
use-restriction. It is ultimately user responsibility to ensure any sensitive,
published data is use available.

#### - local
Locally annotated genomes can be added to the database by filling out and
submitting a `.predb` file using `mtdb predb2db`. `mtdb predb2db` will curate the
inputted data and output into the current directory. Once complete,
`mtdb update --add <PREDB_RESULT>` will add the `.mtdb` generated to the
primary database.

<br /><br /><br />

## Database management

The primary MTDB should be generated from one user, and privileges should be
distributed using `chmod`; e.g. `chmod -R 755`. Note, the primary user/group are the only ones with 
privileges to update and merge manually curated `predb` files into the primary database.

Users should refrain from making edits to database files as unexpected errors
may result with downstream scripts.

<img align="right" src="https://gitlab.com/xonq/mycotools/-/raw/primary/misc/ablogo.png">

<br /><br /><br /><br /><br /><br /><br /><br /><br />

## TODO:

- [x] unify protein id
- [ ] add plant and animal functions