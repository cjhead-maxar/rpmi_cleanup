#!/usr/bin/env bash

if [ $# -eq 0 ]; then
    echo "No arguments provided. Must provide a granule."
    exit 1
fi

GRANULE=$1
LOG="logs/aws_cleanup_shell.log"

archive_bucket="s3://rpmi-archive-us-east-1-production"
gir_archive_bucket="s3://rpmi-archive-us-east-1-production/gir"
prefixes=("PrePro/" "text/" "prior/" "masked")

[[ -d ${GRANULE} ]] || mkdir ${GRANULE}

for prefix in ${prefixes[@]}; do
    local_dir=${GRANULE}/${prefix}
    dir=${archive_bucket}/${GRANULE}/${prefix}

    if [ ${prefix} == "masked" ]; then
        aws s3 mv ${archive_bucket}/${GRANULE}/ \
            ${GRANULE} \
            --recursive \
            --exclude "*" \
            --include "${prefix}*/*.ip3"

    elif [[ ${prefix} == "PrePro/" ]]; then
        aws s3 rm ${dir}

    else
        aws s3 mv ${dir} ${local_dir} --recursive
        aws s3 rm ${dir}
    fi
done

aws s3 mv ${archive_bucket}/${GRANULE}/ \
    ${gir_archive_bucket}/${GRANULE}/ \
    --recursive

tar -cf ${GRANULE}.tar ${GRANULE}
aws s3 mv ${GRANULE}.tar ${gir_archive_bucket}${GRANULE}/

IFS=$'\n' read -d '' -r -a gran_dirs < <(ls ${GRANULE})
for index in ${!gran_dirs[@]}; do
    gran_dirs[$index]="${gran_dirs[$index]}/"
done
tag="TagSet=[{Key=Prefixes,Value='${gran_dirs[@]}'}]"
aws s3api put-object-tagging \
    --bucket "rpmi-archive-us-east-1-production" \
    --key "gir/${GRANULE}/${GRANULE}.tar" \
    --tagging "${tag}"

[[ $? -eq 0 ]] || echo "Error tagging ${GRANULE}.tar" >> ${LOG}
