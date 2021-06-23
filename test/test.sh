#!/usr/bin/bash

# 创建软链

ln -s ~/db_orm /usr/lib/python2.7/site-packages/db_orm

CURR_PATH=$(readlink -f "$(dirname "$0")")

# 测试数据所在路径
TEST_DATA_PATH=$CURR_PATH/test_data

# DB 数据路径
TEST_UNZIP_PATH="/data/db/db/log_data/store/app/"

# db_orm 所在路径
DB_ORM_SOURCE=$(dirname $CURR_PATH)

unzip -d $TEST_UNZIP_PATH $TEST_DATA_PATH/*.zip

export PYTHONPATH=$DB_ORM_SOURCE

python -m db_orm.test.test_orm
