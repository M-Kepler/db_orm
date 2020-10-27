#!/usr/bin/bash

CURR_PATH=$(readlink -f "$(dirname "$0")")

# 测试数据所在路径
TEST_DATA_PATH=$CURR_PATH/test_data

# dap_orm 所在路径
DAP_ORM_SOURCE=$(dirname $CURR_PATH)

# unzip -d $TEST_DATA_PATH $TEST_DATA_PATH/*.zip

export PYTHONPATH=$DAP_ORM_SOURCE

python -m dap_orm.test.test_orm
