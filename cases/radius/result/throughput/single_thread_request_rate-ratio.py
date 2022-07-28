#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from pygnuplot import gnuplot


def load_data(file_name):

    text_file = file_name + ".txt"
    data_file = file_name + ".csv"

    result_file = open(data_file, "w")
    result_file.write("\"requests\",\"count\",\"time\"\n")

    with open(text_file, "r") as open_file:
      for line in open_file:
        l = line.strip()
        if l.startswith("requests:"):
            #print(l.split()[1] + "," + l.split()[3])
            for i in range(80):
                tmp_l = open_file.readline()
                if tmp_l.startswith("real"):
                    result_file.write(l.split()[1] + "," + l.split()[3] + "," + str((datetime.strptime(tmp_l.strip().split()[1], '%Mm%S.%fs')  - datetime(1900, 1, 1) ).total_seconds() ) + "\n")
                    #result_file.write(l.split()[1] + "," + l.split()[3] + "," + str(int(tmp_l.strip().split()[1].split("m")[0]) * 60 + float(tmp_l.strip().split()[1].split("m")[1].split("s")[0])) + "\n")

    result_file.close()

    return pd.read_csv(data_file)


def draw_auth(filename):
    g = gnuplot.Gnuplot()

    # set terminal pdf size 16,9 enhanced font ",18"
    plot_cmd = f'''
    set terminal pdf enhanced font ",18"
    set output '{filename}.pdf'

    color1 = "#29B6F6"; color2 = "#0288D1";

    set style fill solid border lc "black"
    set style boxplot nooutliers
    set boxwidth 0.9

    set style line 1 linecolor rgb color1 linetype 1 linewidth 4 pointtype 5 pointsize 1.2
    set style line 2 linecolor rgb color2 linetype 1 linewidth 4 pointtype 9 pointsize 1.2

    set xtics format ""
    set xlabel "Request Rate"
    set grid ytics
    set ylabel "Throughput Ratio (%)"
    set key top right

    plot "{filename}.dat" using 2:xtic(1) title "SmartNIC" with linespoints linestyle 1,   \
         "{filename}.dat" using 3 title "Server" with linespoints linestyle 2
    '''
    g.cmd(plot_cmd)
    g.close()



output_name = "single_thread_request_rate-ratio"
#output_name = "auth_sha256"
nic_df = load_data("request_rate_single_thread_radperf_nic")
server_df = load_data("request_rate_single_thread_radperf_server")

auth_dat = open(output_name + ".dat", "w")

# for i in range(1,33):
for i in [500,2000,3500,5000,6500,8000,9500]:
    nic_ratio = ((10000. / nic_df.loc[(nic_df["requests"] == i) & (nic_df["count"] == 10000), "time"].mean()) / i) * 100
    server_ratio = ((10000. / server_df.loc[(server_df["requests"] == i) & (server_df["count"] == 10000), "time"].mean()) / i) * 100
    auth_dat.write(str(i) + "\t" + str(nic_ratio) + "\t" + str(server_ratio) + "\n")

auth_dat.close()

draw_auth(output_name)
