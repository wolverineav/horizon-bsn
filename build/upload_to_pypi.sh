#!/bin/bash -eux

# RPM runs as root and doesn't like source files owned by a random UID
OUTER_UID=$(stat -c '%u' /horizon-bsn)
OUTER_GID=$(stat -c '%g' /horizon-bsn)
trap "chown -R $OUTER_UID:$OUTER_GID /horizon-bsn" EXIT
chown -R root:root /horizon-bsn

cd /horizon-bsn
git config --global user.name "Big Switch Networks"
git config --global user.email "support@bigswitch.com"

CURR_VERSION=$(awk '/^version/{print $3}' setup.cfg)

echo 'CURR_VERSION=' $CURR_VERSION
git tag -f -s $CURR_VERSION -m $CURR_VERSION -u "Big Switch Networks"

python setup.py sdist

# force success. but always check if pip install fails
twine upload dist/* -r pypi -s -i "Big Switch Networks" || true
# delay of 5 seconds
sleep 5
sudo -H pip install --upgrade horizon-bsn==$CURR_VERSION
if [ "$?" -eq "0" ]
then
  echo "PYPI upload successful."
else
  echo "PYPI upload FAILED. Check the logs."
fi
# remove the package
sudo -H pip uninstall -y horizon-bsn

# revert the permissions
chown -R $OUTER_UID:$OUTER_GID /horizon-bsn
