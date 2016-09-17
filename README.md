# How to run a local version of IgBLAST without installation

The US National Centre for Biotechnology Information's [IgBLAST](http://www.ncbi.nlm.nih.gov/igblast/ "IgBLAST") tool is a high-performance parser for immunoglobulin and T cell receptor sequences which you can install and run on your own hardware: however it can be complex to install. This repository defines a Docker image for IgBLAST. With Docker installed, you can download and run the image for IgBLAST, or run it on one of a number of cloud platforms, including Amazon Web Services and Azure.

The image has been developed as a prototype for the [AIRR Community](http://airr.irmacs.sfu.ca/). The community is in the process of defining a standard interface for receptor sequence parsers, which will make it easy for users to 'plug and play' in their analysis pipelines. This image will be developed in line with the emerging standard - which is likely to involve some changes to the command syntax along the way. Discussion of the standard and this implementation can be found on the [Community's Forum](http://b-t.cr) and if you are interested we would very much like you to join the forum and participate.

# Functionality

The container implements version 1.6 of IgBLAST. It supports the NCBI's collection of [mouse and rhesus monkey germline genes](http://www.ncbi.nlm.nih.gov/igblast/showGermline.cgi), and [IMGT germline genes](http://imgt.org/genedb/directlinks) for human, mouse, rabbit and rat. IG receptor sequences are provided for all species. T-cell receptor sequences are only provided in the IMGT gene set, and only for human and mouse.

Sequences for analysis should be provided in FASTA format. Output is provided both in IgBLAST report format (-outfmt 3) and in IMGT-style CSV files. Translation to the latter is accomplished via [TrIgs IgBLASTPlus](https://github.com/williamdlees/TRIgS/blob/master/docs/IgBLASTPlus.md). 

The IMGT germline files are downloaded when the container is first used. They are stored in a cache directory for subsequent runs.

# Usage

If Docker is not installed on your machine, installation instructions are available [here](https://www.docker.com/products/overview). It is free to install.

With Docker installed, you can download the IgBlast image with the command

    docker pull williamlees/igblast

The container requires you to create three directories: an input directory, cache directory and output directory. The input directory should contain the sequences for analysis, in a single FASTA format file, and a control file, described in the next section. The other two directories should be empty on first use.

The container is called as follows:

    docker run \
      --volume="input_data:/bbx/mnt/input:ro" \
      --volume="output_data:/bbx/mnt/output:rw" \
      --volume="cache:/bbx/mnt/cache:rw" \
      --rm \
      williamlees/igblast \
      parse

Here:
- `input_data`, `output_data` and `cache` are the full pathnames to the directories that the container will use
- `--rm` tells Docker to delete this instance of the container after it is used (without this, your disk will fill up quickly)
- `williamlees/igblast` is the name of the container
- `parse` is the command to pass to the container

As noted above, the IMGT files are downloaded when the container is first used, and are stored in the cache directory for future use (about 5MB of space is required). You can delete the cache directory at any point between runs, but runs will be faster if it is left intact. You can force the download of a fresh set of IMGT germlines into the cache either by deleting the contents of the cache directory or by using the clean command:

    docker run \
      --volume="input_data:/bbx/mnt/input:ro" \
      --volume="output_data:/bbx/mnt/output:rw" \
      --volume="cache:/bbx/mnt/cache:rw" \
      --rm \
      williamlees/igblast \
      clean

One other command is supported. It will open an interactive session with the container, which may be of interest if you would like to examine files and so on:

    docker run -i -t\
      --volume="input_data:/bbx/mnt/input:ro" \
      --volume="output_data:/bbx/mnt/output:rw" \
      --volume="cache:/bbx/mnt/cache:rw" \
      --rm \
      williamlees/igblast \
      shell


# Control File Format

The control file is placed in the input directory. Its name must be biobox.yaml. It has the following format:

    ---
    version: "0.9.0"
    arguments:
      sequences: <sequence file>
      csvprefix: <prefix>
      igblastfile: <igblast file>
      germline:
        set: <set>
        species: <species>
        receptor: <receptor>

The arguments in <> can take on the following values:

|Value|Option or Meaning|
|-----|-----------------|
|`sequence file`|Filename of the sequence file in the input directory|
|`prefix`|Prefix to use for the filenames of the IMGT-style aa, nn and junction files created in the output directory|
|`igblast file`|Filename of the IgBLAST output file created in the output directory|
|`set`|Germline set to use: either ncbi or imgt|
|`species`|"mouse" for the NIH set, or "human", "mouse", "rabbit" or "rat" for the IMGT set|
|`receptor`|Either "IG" or "TR" ("TR" is only valid for imgt/human, imgt/mouse)|

Example for analysis of rabbit IG sequences using the IMGT germline set:

    ---
    version: "0.9.0"
    arguments:
      sequences: "seqs.fasta"
      outprefix: "result"
      log: "result.txt"
    germline:
      set: imgt
      species: rabbit
      receptor: IG

# Example

The example subdirectory contains sample human heavy chain sequences (taken from the PW99 dataset, Zheng et al., J Clin Invest. 2004) and suitable files for control and execution.

# Restrictions

The container does not support the use of other germline sets. The AIRR Community is defining a standard format for a germline set, and it's intended to introduce support as this standard emerges.

It's currently not possible to tune command-line parameters to IgBLAST.

Alignment is always against the IMGT alignment and field delineation (IgBLAST also supports the Kabat system).

# Implementation

The container follows the [Bioboxes](bioboxes.org) command file standard and is based on a template developed by [Johannes Dröge](https://github.com/fungs?tab=overview&from=2016-08-01&to=2016-08-31&utf8=%E2%9C%93). It is not, formally, a BioBox because there is no RFC for containers of this type, and it is not callable from the [Bioboxes CLI](http://bioboxes.org/docs/command-line-interface/). It is possible that it will develop into a full BioBox over time

# Building the Image

If you wish to make changes and rebuild the docker image, clone this repository. In the top-level directory, type

    docker build -t <name> .

where <name> is the name you wish to give to your container. Push requests are welcome!

