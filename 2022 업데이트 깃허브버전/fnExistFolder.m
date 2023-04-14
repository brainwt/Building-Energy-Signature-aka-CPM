function [checkF] = fnExistFolder( foldername )


%% exist updated folder
checkF=exist(foldername,'dir');

if checkF==7 % folder exist
    
else 
    disp(['[', foldername, ']', ' folder is creatied'])
    mkdir(foldername)
end

end

