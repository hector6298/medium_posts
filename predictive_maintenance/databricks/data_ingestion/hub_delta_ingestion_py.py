# Databricks notebook source
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, DoubleType, IntegerType, StructField

import json

# COMMAND ----------

dbutils.widgets.text("connectionStringEndPoint", '')
dbutils.widgets.text("eventHubName", '')
dbutils.widgets.text("consumerGroup", '')
dbutils.widgets.text("streamDebugMode", 'True')

dbutils.widget

# COMMAND ----------

streamDebugMode = True

# COMMAND ----------

connectionStringEndPoint = "Endpoint=sb://ihsuprodmwhres025dednamespace.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=rkMaaaupaGY/sZ5cYb9Lk/yFy8FGB6+C096jg/DcjEs=;EntityPath=iothub-ehub-telemetry-17003703-f705eeecc7"
eventHubName = "iothub-ehub-telemetry-17003703-f705eeecc7"
consumerGroup = "databricksdelta"

# Create the positions
startingEventPosition = {
  "offset": -1,  
  "seqNo": -1,            #not in use
  "enqueuedTime": None,   #not in use
  "isInclusive": True
}

# COMMAND ----------

ehConf = {
    'eventhubs.connectionString': sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(connectionStringEndPoint),
    'eventhubs.consumerGroup': consumerGroup,
    'eventhubs.startingPosition': json.dumps(startingEventPosition)
}

# COMMAND ----------

df = spark \
  .readStream \
  .format("eventhubs") \
  .options(**ehConf) \
  .load()

# COMMAND ----------

schema = StructType([
    StructField("messageId", IntegerType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True)
])

streamDf = df.select(col("enqueuedTime").alias("enqueued_time"),
                     col("systemProperties.iothub-connection-device-id").alias("device_id"),
                     from_json(col("body").cast("string"), schema).alias("telemetry_json"))\
             .select("enqueued_time", "device_id", "telemetry_json.*")

# COMMAND ----------

streamDf.createOrReplaceTempView("device_telemetry_data")

# COMMAND ----------

finalDf = spark.sql("""
    SELECT messageId, DATE(enqueued_time) as date_enqueued, HOUR(enqueued_time) as hour_enqueued, enqueued_time, device_id, temperature, humidity 
    FROM device_telemetry_data
""")

# COMMAND ----------

if streamDebugMode:
    finalDf.writeStream\
           .format("memory")\
           .queryName("debug_telemetry_data")\
           .start()   
else:
    finalDf.writeStream\
              .outputMode("append")\
              .option("checkpointLocation", "/delta/events/_checkpoints/etl-from-json")\
              .format("delta")\
              .partitionBy("Date_Enqueued", "Hour_Enqueued")\
              .table("delta_telemetry_data")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM debug_telemetry_data

# COMMAND ----------

|
