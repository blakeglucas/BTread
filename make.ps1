$distFolder = '.\dist';

if (Test-Path -Path $distFolder) {
    Remove-Item -r -Force $distFolder;
}

mkdir $distFolder;

cd App;
yarn install;
yarn make;
cd ..\Service;
.\venv\Scripts\activate;
.\build_exe.ps1;
deactivate;
cd ..;
cp .\App\out\BTread-win32-x64\* .\dist\ -Recurse;
cp .\Service\dist\*.exe .\dist\;
cp .\icon.png .\dist\;
