plf_moses.py and plf_hfst.py are programs that:

- identify and segment Swedish compounds
- convert sentences into Python Lattice Format, with expanded word lattices for compound nouns

plf_moses.py segments compounds using the built-in Moses compound splitter.
plf_hfst.py uses the Helsinki Finite State Transducer's output.
	- The Swedish transducer can be downloaded at: https://hfst.github.io/

The output can be verified with Moses's built in plfcheck before being directly input into  the Moses translation system.
