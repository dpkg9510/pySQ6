# Move the generated .png job previews to the archiving directory.
@echo off

set "sourceFolder=INSTALLATION_DIRECTORY\SafeQ6\FSP\Service\JobStore"
set "destinationFolder=ARCHIVING_DIRECTORY"

echo Copying .png files from %sourceFolder% to %destinationFolder%...

for %%F in ("%sourceFolder%\*.png") do (
    copy "%%F" "%destinationFolder%\"
)

echo All .png files have been copied.