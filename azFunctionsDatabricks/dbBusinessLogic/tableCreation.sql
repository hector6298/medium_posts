-- Databricks notebook source
CREATE OR REPLACE TABLE yellow_trip_data (
  VendorID string,
  tpep_pickup_datetime date,
  tpep_dropoff_datetime date,
  passenger_count int
)

-- COMMAND ----------

-- MAGIC %python
-- MAGIC dbutils.fs.mount(
-- MAGIC   source = "wasbs://<container>@<storage-account>.blob.core.windows.net",
-- MAGIC   mount_point = "/mnt/test",
-- MAGIC   extra_configs = {"fs.azure.account.key.<storage-account>.blob.core.windows.net":"<storage-acount-key"})

-- COMMAND ----------

-- MAGIC %sh 
-- MAGIC ls /dbfs/mnt/test

-- COMMAND ----------


