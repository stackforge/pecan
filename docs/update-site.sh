make html
rm -rf ../../pecan.github.com/docs
cp -r build/html ../../pecan.github.com/docs
cd ../../pecan.github.com
git commit -a -m "Updating documentation."
git push
