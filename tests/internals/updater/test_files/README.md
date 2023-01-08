# Test Files

## Update Contents

- **test-package1_0.1.0-0_all.deb** - A basic deb package (install a txt file)
with no dependencies
- **test-package2_0.1.0-0_all.deb** -  Another basic deb package (install a
different txt file) that depends on test-package1
- **test-script.sh** - A bash script used in test update tar files.

## Valid Updates

- **test_update_1611940000.tar.xz** - Installs test-package1 and test-package2
then run a bash script.
- **test_update_1611941111.tar.xz** - Removes test-package2 and
test-package1.
- **test_update_1611942222.tar.xz** - Only installs test-package2 (can be
a invalid update if test-package1 is not installed).

## Invalid Updates

- **test_update_1611943333.tar.xz** - missing instructions.txt in tar
- **test_update_1611944444.tar.xz** - missing .deb file in tar
- **test_update_1611945555.tar.xz** - missing script in tar
- **test_update_1611946666.tar.xz** - invalid JSON contexts from instructions.txt
- **test_update_1611947777.tar.xz** - invalid instructions.txt format (not a JSON)
- **test_update_1611948888.tar.xz** - invalid .tar.xz file
