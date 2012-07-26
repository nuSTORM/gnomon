FILENAME=ConfigurationSchema.json
cat $FILENAME | python -mjson.tool > ${FILENAME}2
mv ${FILENAME}2 $FILENAME