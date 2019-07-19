# Shell Scripts

There are a number of shell scripts included in **Topaz3**.

They mainly serve as an interface to command line tools provided by [CCP4](http://www.ccp4.ac.uk/).

However, they are most likely specific to use at Diamond and will therefore require alterations to work properly
on other machines.

Let's take a look at *topaz3/shell_scripts/cfft.sh*:

```bash
#!/bin/bash

module load ccp4

cfft "$@"
```

This script does nothing other than load a specific module and call *cfft* with the parameters that are
passed into it.

If *cfft* is installed directly on your machine, or is available through a different evironment,
change the "**module load ...**" line so that it works for you.
This may involve simply removing it.

It should be possible to test that this is working by running:

```bash
topaz3/shell_scripts/cfft.sh --help
```

which should connect to your installation of *cfft* and show the help information.

This shell script should now work properly within the data transformation pipeline.

Simply repeat this process for the other shell scripts.