import pandas as pd
import plotly.graph_objects as go
import streamlit as st

df_raw = pd.read_csv("test_2.csv", sep=";")

#creating the sdg column with a dummy value
df_raw["sdg"] = 0

#assigning the sdg columns its respective value
#there is only 16 sdgs in this table
for i in range(1,19):
    df_raw.loc[df_raw[f'SDG {i}']==1,["sdg"]] = i

#creating a new dataframe by removing the SDG ... columns
df = df_raw.loc[:, ["Authors", "Title", "Year", "EID", "sdg"]]

#grouping the EID to see in how many sdgs they are
df_grouped = df.groupby('EID')[['sdg']].count()

#identifying those eids present in more than one sdg and storing them in a new dataframe
df_duplicates = df_grouped.loc[df_grouped["sdg"] > 1,]
#droping the index, which is the EID, and putting it as a column
df_duplicates = df_duplicates.reset_index(drop=False)
#changing the name of the columng sdg
df_duplicates = df_duplicates.rename(columns={'sdg': 'in_how_many_sdgs_appear?'})

#merging the duplicates dataframe with df2. The df_sub stands for dataframe subselected
df_sub = pd.merge(df, df_duplicates, on='EID', how='inner')
#sorting the columns
df_sub = df_sub.sort_values(by=["in_how_many_sdgs_appear?", "EID", "sdg"], ascending=True)
#reseting the index
df_sub= df_sub.reset_index(drop=True)

#function duplicates table for each sdg
def duplicates_by_sdg(sdg_number):
    #subselecting the df_sub for the respective sdg
    sdg = df_sub.loc[df_sub["sdg"]==sdg_number,]
    #merging the the sdg dataframe with df_sub
    sdg_d = pd.merge(df_sub, sdg, on='EID', how='inner')
    #selecting only the relevant columns
    sdg_d = sdg_d.iloc[:,0:6]
    #selecting only those rows where the sdg number is different from the respective sdg
    sdg_duplicate = sdg_d.loc[sdg_d["sdg_x"] != sdg_number,]
    #
    sankey_df = pd.merge(sdg, sdg_duplicate, on='EID', how='inner')[["Authors", "Title", "Year", "EID", "sdg", "in_how_many_sdgs_appear?", "sdg_x"]]
    sankey_df = sankey_df.rename(columns={'in_how_many_sdgs_appear?': 'duplicates','sdg_x': 'also_in_sdg'})
    sankey_df["duplicates"] = sankey_df["duplicates"] - 1

    sankey_df["Year"] = sankey_df["Year"].astype(str)
    return sankey_df

#function sankey table for each sdg
def sankey_table(sdg):
    df = duplicates_by_sdg(sdg)
    #sorting the dataframe according to the other present sdgs
    sank = df.sort_values(by="also_in_sdg", ascending = True)
    #grouping the column "also in sdg" to get the occurence of them
    sank = sank.groupby("also_in_sdg")[["sdg"]].count()["sdg"]
    #reseting the index
    sank = sank.reset_index(drop=False)
    #adding the source column
    sank["source"] = str(sdg)
    #changing the name of the other columns to sankey_diagram_format
    sank = sank.rename(columns={'also_in_sdg': 'target','sdg': 'value'})
    #converting the target column to string
    sank["target"] = sank["target"].astype(str)

    return sank

#function sankey diagram for each sdg
def sankey_diagram(sdg):
    try: 
        df = sankey_table(sdg)
        #creating list that will go to the sankey diagram
        label = []
        source = []
        value = []
        target = []
    
        #adding the values to the lists
        label.append(df.loc[0, "source"])
        for i in range(df.shape[0]):
            label.append(df.loc[i, "target"])
            source.append(0)
            target.append(i+1)
            value.append(df.loc[i,"value"])
    
        #creating the diagram
        fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=100,
            thickness=20,
            line=dict(color="black", width=0.5),
            label= label
        ),
        link=dict(
            source=source,  # Source node IDs
            target=target,  # Target node IDs
            value=value,     # Link values
            #color = 'rgba(255, 127, 14, 0.7)'
        )
        )])
    
        # Update layout settings
        fig.update_layout(title_text=f"Sankey Diagram for sdg {sdg}", font_size=10)
    
        # Show the plot
        return fig
        
    except KeyError:
        fig = 0
        return fig


#sankey diagram function with overlaps

def sankey_diagram_overlap():
    
    label = []
    source = []
    value = []
    target = []
    colores = []
    colors = ['rgba(31, 119, 180, 0.7)', 
              'rgba(255, 127, 14, 0.7)', 
              'rgba(44, 160, 44, 0.7)', 
              'rgba(214, 39, 40, 0.7)', 
              'rgba(148, 103, 189, 0.7)', 
              'rgba(140, 86, 75, 0.7)', 
              'rgba(227, 119, 194, 0.7)', 
              'rgba(127, 127, 127, 0.7)', 
              'rgba(188, 189, 34, 0.7)', 
              'rgba(23, 190, 207, 0.7)', 
              'rgba(174, 199, 232, 0.7)', 
              'rgba(255, 187, 120, 0.7)', 
              'rgba(152, 223, 138, 0.7)', 
              'rgba(255, 152, 150, 0.7)', 
              'rgba(197, 176, 213, 0.7)', 
              'rgba(196, 156, 148, 0.7)',
              'rgba(31, 119, 180, 0.7)',
              'rgba(255, 127, 14, 0.7)']
    
    for j in range(1,19):
    
        try:
    
            dff = sankey_table(j)
            dff["source"] = "sdg_s " + dff["source"]
            dff["target"] = "sdg_t " + dff["target"]
            #creating list that will go to the sankey diagram
        
            #adding the values to the lists
            label.append(dff.loc[0, "source"]) #
            for i in range(dff.shape[0]):
                if dff.loc[i, "target"] in label:
                    label = label
                else:
                    label.append(dff.loc[i, "target"])
                index_source = label.index(f"sdg_s {j}")
                source.append(index_source)
                index_target = label.index(dff.loc[i, "target"])
                target.append(index_target)
                value.append(dff.loc[i,"value"])
                colores.append(colors[j-1])
                
        except KeyError:
            pass
            
    fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=100,
        thickness=20,
        line=dict(color="black", width=4.5),
        label= label,
        #color = colores
    ),
    link=dict(
        source=source,  # Source node IDs
        target=target,  # Target node IDs
        value=value,     # Link values
        color = colores
    )
    )])
    
    # Update layout settings
    fig.update_layout(title_text=f"Sankey diagram for all duplicates", font_size=10, height=1500, width=800)
    
    # Show the plot
    return fig



st.title('SDGs DUPLICATES')

st.write('General overview of all duplicates')
st.write(''' *sdg_s* means sdg source and *sdg_t*, sdg target.

*Source* and *Target* are specific terminology for sankey diagrams. Therefore, this notation was used


''')
overlap = sankey_diagram_overlap()
st.plotly_chart(overlap, use_container_width=True)



# User input for parameter
sdg_list = df["sdg"].unique().tolist()
sdg_list = sorted(sdg_list)
st.write('Duplicates for specific sdg')

sdg = st.selectbox('Select your sdg:', sdg_list)
sdg = int(sdg)

#generate Sankey per sdg
fig = sankey_diagram(sdg)

if fig == 0:
    st.write("This SDG has no duplicates")

else:
    st.plotly_chart(fig, use_container_width=True)


# Generate DataFrame based on parameter
dataframe = duplicates_by_sdg(sdg)
dataframe = dataframe[["EID", "duplicates", "also_in_sdg", "Title", "Authors", "Year"]]

# Display DataFrame
st.write('Generated DataFrame:')
st.write(dataframe)