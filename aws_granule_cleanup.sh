#!/usr/bin/env bash

if [ $# -eq 0 ]; then
    echo "No arguments provided. Must provide a granule."
    exit 1
fi

GRANULE=$1

archive_bucket="s3://rpmi-archive-us-east-1-production/"
gir_archive_bucket="s3://rpmi-archive-us-east-1-production/gir/"

prefixes=("text/" "prior/" "masked")

[[ -d ${GRANULE} ]] || mkdir ${GRANULE}

for prefix in ${prefixes[@]}; do
    local_dir=${GRANULE}/${prefix}
    dir=${archive_bucket}${GRANULE}/${prefix}

    [[ -d ${local_dir} ]] || mkdir ${local_dir}

    if [ ${prefix} = "masked" ]; then
        aws s3 mv ${dir} ${local_dir} --recursive --exclude "*" --include "*.ip3"
    else
        aws s3 mv ${dir} ${local_dir} --recursive
        aws s3 rm ${dir}
    fi
done

aws s3 mv ${archive_bucket}${GRANULE}/ ${gir_archive_bucket}${GRANULE}/ --recursive

tar -cf ${GRANULE}.tar ${GRANULE}
aws s3 mv ${GRANULE}.tar ${gir_archive_bucket}${GRANULE}/
