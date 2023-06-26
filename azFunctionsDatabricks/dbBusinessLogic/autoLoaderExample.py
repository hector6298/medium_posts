# Databricks notebook source
dbutils.widgets.text("table_name", '')
dbutils.widgets.text("data_source", '')
dbutils.widgets.text("checkpoint_directory", '')

# COMMAND ----------

table_name = dbutils.widgets.get("table_name")
data_source = dbutils.widgets.get("data_source")
checkpoint_directory = dbutils.widgets.get("checkpoint_directory")

# COMMAND ----------

def autoload_to_table(data_source, source_format, table_name, checkpoint_directory):
    query = (spark.readStream
                  .format("cloudFiles")
                  .option("cloudFiles.format", source_format)
                  .option("cloudFiles.schemaLocation", checkpoint_directory)
                  .option("cloudFiles.schemaHints", 
                          """VendorID string, 
                             tpep_pickup_datetime date, 
                             tpep_dropoff_datetime date, 
                             passenger_count int""")
                  .load(data_source)
                  .select(["VendorId", 
                           "tpep_pickup_datetime", 
                           "tpep_dropoff_datetime", 
                           "passenger_count"])
                  .writeStream
                  .option("checkpointLocation", checkpoint_directory)
                  .trigger(availableNow=True)
                  .table(table_name))
    return query

query = autoload_to_table(data_source = data_source,
                          source_format = "csv",
                          table_name = table_name,
                          checkpoint_directory = checkpoint_directory)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM default.yellow_trip_data

# COMMAND ----------


