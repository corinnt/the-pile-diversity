import pygmt
import util

def map_points(df, name): 
    """ Maps longitude and latitude points on a map of the globe

        :param df: dataframe with cols longitude, latitude, and counts (for repeats) 
        :param name: name for the map PNG in the output folder
        
    alternate region based on data, but globe looks cleaner
    region = [
        df.longitude.min() - 1,
        df.longitude.max() + 1,
        df.latitude.min() - 1,
        df.latitude.max() + 1,
        ]
    """
    region = [-180, 180, -60, 80] # frame all major continents
    util.info(df.head())
    

    fig = pygmt.Figure()
    fig.basemap(region=region, projection="M8i", frame=True)
    fig.coast(land="black", water="skyblue")
    fig.plot(x=df.longitude, y=df.latitude, style="c0.3c", fill="black", pen="black")
 
    fig = pygmt.Figure()
    fig.basemap(region=region, projection="M8i", frame=True)
    fig.coast(land="lightblue", water="white")
    fig.plot(
        x=df.longitude,
        y=df.latitude,
        size=0.09 * df.counts,
        style="cc",
        fill="black",
        #pen="gray40",
        transparency=45
    )
    fig.savefig("../output/" + name + ".png")
    
