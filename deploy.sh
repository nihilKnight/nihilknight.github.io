rm -rf build/
source .venv/bin/activate
python3 freezer.py
deactivate

cd ../pages/
git checkout deploy_try
mv .git/ ../
rm -rf *
cp -r ../blog_flask/* ./
mv ../.git/ ./
git add .
git commit -m "updated pages."
git push 
git checkout main
cd ../blog_flask/
