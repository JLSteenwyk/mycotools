import setuptools

with open( "README.md", "r" ) as fh:
    long_description = fh.read()

setuptools.setup(
    name = "mycotools",
    version = "0.3.0b3",
    author = "xonq",
    author_email = "konkelzach@protonmail.com",
    description = "A compilation of bioinformatic and computation biology inspired " + \
        "python tools",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://gitlab.com/xonq/mycotools/mycotools",
    packages = setuptools.find_packages( ),
    scripts = ['mycotools/abstractHmm.py', 'mycotools/acc2fa.py', 'mycotools/acc2gff.py', 'mycotools/annotationStats.py', 'mycotools/assemblyStats.py', 'mycotools/curAnnotation.py', 'mycotools/db2hmmsearch.py', 'mycotools/grabClusters.py', 'mycotools/jgiDwnld.py', 'mycotools/ncbiDwnld.py', 'mycotools/proteomeStats.py', 'mycotools/curProteomes.py', 'mycotools/queryDB.py', 'mycotools/ncbi2db.py', 'mycotools/abstractDB.py', 'mycotools/predb2db.py', 'mycotools/updateDB.py', 'mycotools/jgi2db.py', 'mycotools/dbFiles.py', 'mycotools/gff2gff3.py', 'mycotools/curGFF3.py'],
    install_requires = [ 'biopython', 'pandas', 'requests', 'scikit-learn' ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires = ['>=3.0', '<4']
)
