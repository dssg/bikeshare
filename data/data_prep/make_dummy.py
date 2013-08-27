# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

def make_dummy_inner(column_names_list, data_frame, part_of_time, time_lag, ref_var_num = None, num_of_levels = None):
    import patsy
    from patsy.contrasts import Treatment
    import pandas as pd
    # Strip month information from original timestamp variable
    exec "time = pd.DatetimeIndex(data_frame.index)." + part_of_time
    
    #drop first row because of lagged variable

    if str(part_of_time) != "weekday":
        # Create contrast matrix
        levels = range(num_of_levels)
        contrast = Treatment(reference=ref_var_num).code_without_intercept(levels)
        # Encode dummy matrix
        if str(part_of_time) == "month":
            time_dummy = contrast.matrix[time-1, :] # This takes into account that month is coded 1 to 12
        else:
            time_dummy = contrast.matrix[time, :] # This holds for hour since 1 a.m. is coded 0
        #time_dummy_lagged = time_dummy[time_lag:, :]
        time_dummy_lagged = time_dummy[:, :]
    # This j skips the column for the" reference level in the contrast matrix
        j = 0
        for i in range(num_of_levels):
            if i != ref_var_num:
                data_frame[column_names_list[i]] = time_dummy_lagged[:,i-j]
            else:
                j = 1
    # Generate weekday dummy variable
    else:
        weekday_dummy = []
        #for i in range(time_lag,len(time)):
        for i in range(0,len(time)):
            if time[i] < 5:
                weekday_dummy.append(1)
            else:
                weekday_dummy.append(0)
        data_frame["weekday"] = weekday_dummy
    return data_frame

# <codecell>

def make_dummy(data_frame, part_of_time):
    if part_of_time == "hour":
        cat_df = make_dummy_inner(['0hr', '1hr', '2hr', '3hr', '4hr', '5hr', '6hr', '7hr', '8hr', '9hr', '10hr', '11hr', '12hr', '13hr', '14hr', '15hr', '16hr', '17hr', '18hr', '19hr', '20hr', '21hr', '22hr', '23hr'], data_frame, "hour", 3, 0, 24)
    if part_of_time == "weekday":
        cat_df = make_dummy_inner(["weekday"], data_frame, "weekday", 3)
    return cat_df

# <codecell>


# <codecell>


# <codecell>


# <codecell>



# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


