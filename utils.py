from google.cloud import storage
from google.oauth2 import service_account
import streamlit as st
import tensorflow as tf
import numpy as np


LOCAL_API_DATA_FOLDER = ""
MAPS_API_KEY = st.secrets["MAPS_API_KEY"]

dim_dict = {
    "unet":(200,200,3),
    "segnet":(200,200,3),
    "DeepLabV3":(512,512,3)
}

@st.cache_resource
def get_model_from_gcs(model="unet"):

    print("Getting new model!")

    credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
    )

    client = storage.Client(project="wagon-taxi-cab", credentials=credentials)
    buckets = client.list_buckets()

    bucket_name = 'taxifare_paukhard'
    directory_name = 'unet'
    destination_folder = 'unet'

    bucket = client.get_bucket(bucket_name)

    blob_iterator = bucket.list_blobs()

    blob = bucket.blob(f"models/{model}.h5")

    blob.download_to_filename("model")
    model = tf.keras.models.load_model("model")

    return model

def compute_iou(mask1, mask2):
    """
    Compute the Intersection over Union (IoU) of two binary segmentation masks.

    Args:
        mask1 (numpy.ndarray): First binary mask.
        mask2 (numpy.ndarray): Second binary mask.

    Returns:
        float: IoU score.
    """
    # Ensure the masks are binary
    mask1 = (mask1 > 0).astype(np.uint8)
    mask2 = (mask2 > 0).astype(np.uint8)

    # Intersection and Union
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()

    # Avoid division by zero
    if union == 0:
        return 0.0

    return intersection / union
