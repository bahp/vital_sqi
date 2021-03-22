import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler,MinMaxScaler
import scipy
from scipy.signal import argrelextrema
from scipy import signal
import os
import sys
sys.path.append("..")
import plotly.graph_objects as go
import plotly.io as pio

from utilities.peak_approaches import waveform_template

try:
    from ..utilities.filtering import butter_lowpass_filter,butter_highpass_filter,\
        smooth,scale_pattern,smooth_window,get_clipping_pivots
    from ..utilities.generate_template import custom_window
except:
    from utilities.filtering import butter_lowpass_filter,butter_highpass_filter,\
        smooth,scale_pattern,smooth_window
    from utilities.generate_template import custom_window

try:
    from ..sqi.SQI import dtw_sqi,kurtosis_sqi,skewness_sqi,zero_crossings_rate_sqi,entropy_sqi,signal_to_noise_sqi
except:
    from sqi.SQI import dtw_sqi,kurtosis_sqi, skewness_sqi, zero_crossings_rate_sqi, entropy_sqi, signal_to_noise_sqi


def tapering(signal_data,scan_window = 100):
    local_minima = argrelextrema(signal_data, np.less)

    signal_data = signal_data-np.min(signal_data)
    window = signal.windows.tukey(len(signal_data),0.9)
    signal_data_tapered = np.array(window) * (signal_data) #-min(signal_data)
    return np.array(signal_data_tapered)

sqi_dict = {
        'kurtosis_sqi': [],
        'skewness_sqi': [],
        'entropy_sqi': [],
        'signal_to_noise_sqi': [],
        'zero_crossings_rate_sqi': [],
        'dtw_template1':[],
        'dtw_template2':[],
        'dtw_template3':[]
}
sqi_methods = [kurtosis_sqi,
                   skewness_sqi, entropy_sqi,
                   signal_to_noise_sqi,
                   zero_crossings_rate_sqi,
                    dtw_sqi,
                    dtw_sqi,
                    dtw_sqi
               ]
if __name__ == "__main__":

    waveform = waveform_template()
    pio.renderers.default = "browser"

    DATA_PATH = os.path.join(os.getcwd(), "..", "data", "11")  # 24EI-011-PPG-day1-4.csv
    filename = "24EI-011-PPG-day1"  # 24EI-011-PPG-day1
    ROOT_SAVED_FOLDER = os.path.join(os.getcwd(),"..","data","label_PPG_segment")
    SAVED_FOLDER = os.path.join(ROOT_SAVED_FOLDER,filename)
    SAVED_FILE_FOLDER = os.path.join(SAVED_FOLDER,"ppg")
    SAVED_LABEL_FOLDER = os.path.join(ROOT_SAVED_FOLDER, "..","waveform_analysis")
    IMG_FOLDER = os.path.join(SAVED_LABEL_FOLDER, "img")
    TEMPLATE_FOLDER = os.path.join(SAVED_LABEL_FOLDER, "template")
    ANALYSIS_FOLDER = os.path.join(SAVED_LABEL_FOLDER, "analysis")

    df_label = pd.read_csv(os.path.join(SAVED_LABEL_FOLDER,os.listdir(SAVED_LABEL_FOLDER)[1]),header=0)
    short_list = np.array(df_label["file_name"])

    files = [os.path.join(SAVED_FILE_FOLDER,f) for f in os.listdir(SAVED_FILE_FOLDER)
             if f in short_list]# if os.isfile(os.path.join(ROOT_SAVED_FOLDER, f))]
    print(files)

    """
    Load data -> lowpass filter x2  
    Standard scale or MinMax scale on the whole segment
    cut data using trough peak detection,
    Taper -> Confirm
    Squeezing and Spanning 
    
    """
    for file in files:
        sig = np.loadtxt(file, delimiter=',', unpack=True)
        sig = butter_highpass_filter(sig, cutoff=1, fs=100, order=1)
        sig = butter_highpass_filter(sig, cutoff=1, fs=100, order=1)
        scaler = StandardScaler()
        sig = scaler.fit_transform(sig.reshape(-1,1)).reshape(-1)

        peak_shortlist, trough_shortlist = waveform.detect_peak_trough_count_orig(sig)

        width = np.median(np.diff(trough_shortlist))
        template = []
        fig = go.Figure()
        fig.update_layout(
            title=file.split("\\")[-1],
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        for left_trough,right_trough in zip(trough_shortlist[:-1],trough_shortlist[1:]):
            segment = sig[left_trough:right_trough+1]
            segment_taper = tapering(segment)
            if (len(segment_taper)<2*width):
                segment_taper = scale_pattern(segment_taper, width)
                template.append(segment_taper)
                fig.add_traces(go.Scatter(x=np.arange(1, width),
                                          y=segment_taper, mode="markers"))
            else:
                segments = []
                segments = segments + [segment_taper[int(width * i):int(width * (i + 1))]
                                       for i in range(0, int(np.ceil(len(segment_taper) / width)))]

                for seg in segments:
                    segment_taper = scale_pattern(seg, width)
                    template.append(segment_taper)
                    fig.add_traces(go.Scatter(x=np.arange(1, width),
                                              y=segment_taper, mode="markers"))
        # fig.show()

        template_mean = (np.mean(np.array(template), axis=0))
        fig.add_traces(go.Scatter(x=np.arange(1, width),
                                  y=template_mean, mode="lines"))
        # fig.show()
        fig.write_image(os.path.join(IMG_FOLDER, file.split("\\")[-1].split(".")[0] + '.png'))
        # print(template_mean)
        """
        Compute the sqi and append to the dataframe
        """
        for sqi_method,sqi_name in zip(sqi_methods,sqi_dict.keys()):
            # row_content.append(sqi_method(np.array(template)))
            if sqi_name == 'dtw_template1':
                sqi_dict[sqi_name].append(sqi_method(template_mean,0))
            elif sqi_name == 'dtw_template2':
                sqi_dict[sqi_name].append(sqi_method(template_mean,1))
            elif sqi_name == 'dtw_template3':
                sqi_dict[sqi_name].append(sqi_method(template_mean,2))
            else:
                sqi_dict[sqi_name].append(sqi_method(template_mean))


        saved_filename = file.split("\\")[-1].split(".")[0]
        mmscaler = MinMaxScaler()

        np.savetxt(os.path.join(TEMPLATE_FOLDER, saved_filename + '.csv'),
                   MinMaxScaler().fit_transform(template_mean.reshape(-1,1)), delimiter=',')  # as an array

    for sqi_name in sqi_dict.keys():
        df_label[sqi_name] = sqi_dict[sqi_name]
    df_label.to_csv(os.path.join(ANALYSIS_FOLDER,filename+"-analysis.csv"))