def getValidTrips(df_raw):
    
    # convert hours to minutes
    df_raw['OutgoingTrip_TripDuration_Minutes'] = df_raw.OutgoingTrip_TripDuration.astype(float) / 60
    df_raw['ReturnTrip_TripDuration_Minutes'] = df_raw.ReturnTrip_TripDuration.astype(float) / 60

    # let's see quantiles to check for anomalies
    print(df_raw.quantile([.05, .95], axis = 0) )

    # let's remove the trips with distance travelled 0
    print("Before filtering:")
    print(df_raw.shape)
    df = df_raw[(df_raw['OutgoingTrip_DistanceTravelled'] > 0.3) & (df_raw['OutgoingTrip_TripDuration_Minutes'] < 120)]
    df = df[(df_raw['ReturnTrip_DistanceTravelled'] > 0.45) & (df_raw['ReturnTrip_TripDuration_Minutes'] < 120)]
    df = df[(df_raw['OutgoingTrip_TripDuration_Minutes'] < df_raw['OutgoingTrip_DistanceTravelled'] * 10)]
    print("After filtering:")
    print(df.shape)
    return df

def render_mpl_table(data, figpath, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, rowLabels=data.index.values, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors)])
    plt.savefig(figpath, bbox_inches="tight")
    return ax