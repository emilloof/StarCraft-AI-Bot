% Plot all time logs
close all
files = dir('log*');
for i=1:length(files)
    figure('Name',files(i).name);
    log = readtable(files(i).name);
    time = log{:,"frame"}/24;
    plot(time,log{:,"main"});
    hold on
    state_l = plot(time,log{:,"state"});
    plot(time,log{:,"units"}/max(log{:,"units"}));

    are = area(time,log{:,"assign_thread"});
    are.FaceAlpha = 0.2;
    are.EdgeColor = [1 1 1];

    yline(mean(log{:,"main"}));
    % yline(mean(log(log(:,3)==1,2)));
    title(files(i).name);
end