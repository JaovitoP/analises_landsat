def show_detections_per_day(df):
    total_por_dia = df.groupby('data').size().reset_index(name='Total de detecções').rename(columns={'data':'Data'})
    
    display(total_por_dia)