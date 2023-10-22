import pandas as pd
import PySimpleGUI as sg
import numpy as np
from sklearn.linear_model import LinearRegression
# Define the GUI layout
layout = [
    [sg.Text("Select a CSV file to correct:")],
    [sg.Input(), sg.FileBrowse()],
    [sg.Radio("Hedley", "RADIO1", default=True), sg.Radio("Cox-Munk", "RADIO1")],
    [sg.Button("Correct"), sg.Button("Cancel")]
]

# Create the PySimpleGUI window
window = sg.Window("Sun glint Correction Tool", layout, size=(600, 400))

# Start the event loop
while True:
    event, values = window.read()
    if event in (None, "Cancel"):
        break

    # Read the CSV file
    filename = values[0]
    image_data  = pd.read_csv(filename)

    # Select the correction method
    if values[1]:
        # Method 1
        # ...
        band_columns = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B10", "B11", "B12"]
        id_column = "id"
        mapx_column = "mapx"
        mapy_column = "mapy"
        lat_column = "lat"
        lon_column = "lon"

        # Define the NIR band to use for the deglinting correction
        nir_band = "B8"

        # Define the sample region to use for the deglinting correction (e.g. deep water areas)
        sample_region = image_data[image_data[nir_band] < 0.1]

        # Calculate the minimum NIR radiance in the sample region
        nir_min = sample_region[nir_band].min()

        # Loop through each band and perform the deglinting correction
        for band in band_columns:
            # Skip the NIR band, as it is used as the reference for the correction
            if band == nir_band:
                continue

            # Calculate the linear regression between the NIR and band radiance in the sample region
            X = sample_region[nir_band].values.reshape(-1, 1)
            y = sample_region[band].values.reshape(-1, 1)
            reg = LinearRegression().fit(X, y)
            slope = reg.coef_[0][0]

            # Perform the deglinting correction for each pixel in the image
            image_data[band] = image_data[band] - slope * (image_data[nir_band] - nir_min)

        # Save the corrected image data to a CSV file
        #image_data.to_csv("corrected_image.csv", index=False)
        #output_file_path = "corrected_image.csv"
        # Save the corrected data to a new CSV file
        output_filename = "output_method1.csv"
        image_data.to_csv(output_filename, index=False)
    else:
        # Method 2
        # ...
        
        band_columns = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B10", "B11", "B12"]
        bands = image_data[band_columns].values

        # Compute the correction factor for each band
        wave_lengths = [443.9, 496.6, 560.0, 664, 703.9, 740.2, 782.5, 835.1, 864.8, 945.1, 1373.5, 1613.7, 2202.4]
        corr_factor = np.ones(len(band_columns))

        for i, wave_length in enumerate(wave_lengths):
              theta = np.arcsin(0.05)
              gamma = np.arcsin(0.2)
              r0 = 0.5
              corr_factor[i] = ((np.exp(-2 * ((np.pi * r0) / wave_length) * np.sin(theta)**2)) / 
                      (np.exp(-2 * ((np.pi * r0) / wave_length) * np.sin(gamma)**2)))

        # Reshape the correction factor array to match the shape of the bands array
        corr_factor = np.tile(corr_factor, (bands.shape[0], 1))

        # Apply the correction factor to the bands
        corrected_bands = bands / corr_factor

        # Replace the band columns in the image DataFrame with the corrected bands
        image_data[band_columns] = corrected_bands


        # Save the corrected image data to a CSV file
        #image_data.to_csv("cox_rrected_image.csv", index=False)
        #df2=pd.read_csv("cox_rrected_image.csv")
        # Save the corrected data to a new CSV file
        output_filename = "output_method2.csv"
        image_data.to_csv(output_filename, index=False)

    # Show a popup message with the output filename
    sg.popup(f"Output saved to {output_filename}")

# Close the window
window.close()
