#!/bin/bash
echo "Step 02."
cd $APP_PATH/
marker_file="marker_file_step_02"

if [ -f "marker_file" ]; then
    echo "$marker_file exist"
else
    cp src/collab/static/collab/img/default.png media/
    cp src/collab/static/collab/img/logo.png media/
    echo "Collect static"
    echo "Copy file(s) in static root directory [$(python manage.py collectstatic --noinput | wc -l)]"
    sleep $TIME_SLEEP
    echo "Ok" > $marker_file
fi
echo "$(basename $0) complete."
