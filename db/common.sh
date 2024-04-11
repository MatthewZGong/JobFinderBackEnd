# Some common shell stuff.

echo "Importing from common.sh"

DB=SWE_DESIGN_PROJECT
USER=GroupConnect
CONNECT_STR="mongodb+srv://cluster0.mpx0yi5.mongodb.net/"
if [ -z $DATA_DIR ]
then
    DATA_DIR=~/JobFinderBackEnd/db
fi
BKUP_DIR=$DATA_DIR/bkup

echo "Must add mongoexport and mongoimport to path"
EXP=mongoexport
IMP=mongoimport

if [ -z $MONGO_PASSWORD ]
then
    echo "You must set MONGO_PASSWORD in your env before running this script."
    exit 1
fi

declare -a Collections=("jobs" "users" "user_reports")