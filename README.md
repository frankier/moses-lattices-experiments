# moses-udpipe-lattices
To run tagging.py you need the following requirements (Debian/Ubuntu/Linux Mint packages given)
 * default-jdk
 * ant
 * jflex

You will also need the stagger data file:

    $ wget http://mumin.ling.su.se/projects/stagger/swedish.bin.bz2
    $ bunzip2 swedish.bin.bz2

You can run stagger manually like so
    $ cd stagger
    $ java -Xxmx4g -jar stagger.jar -modelfile ../swedish.bin -posBeamSize 200 -multiple 30 -tag -
