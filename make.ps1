$distFolder = '.\dist';

if (Test-Path -Path $distFolder) {
    Remove-Item -r -Force $distFolder;
}

mkdir $distFolder;

cd App;
yarn install;
yarn make;

cd ..\Service;

if (-not (Test-Path -Path '.\venv')) {
    python -m virtualenv venv;
}

.\venv\Scripts\activate;
pip install -r requirements.txt;
.\build_exe.ps1;
deactivate;
cd ..;
cp .\App\out\BTread-win32-x64\* .\dist\ -Recurse;
cp .\Service\dist\*.exe .\dist\;
cp .\icon.png .\dist\;
