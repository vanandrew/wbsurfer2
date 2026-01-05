%
% Example MATLAB script to parse a path from the wb_surfer2 command
%


clc;
clear;
close all;

% choose the scene file and the row indices to parse
scene_file = 'tests/data/dtseries.scene';
row_indices = [15000 15005];

% format the system command to parse the rows
row_indices_str = num2str(row_indices);
[~, rows_str] = system(['wb_surfer2 -s ' scene_file ' -n test --print-rows ' row_indices_str]);

% convert to array and display
rows = str2num(rows_str);
display(rows(1:end));
