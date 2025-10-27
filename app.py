import streamlit as st
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import warnings

# --- Page Config ---
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="centered"
)

# Suppress warnings from matplotlib
warnings.filterwarnings("ignore")

# --- Sidebar ---
st.sidebar.title("Analyze Your Chat")

st.sidebar.markdown("---")
st.sidebar.caption("How to use:")
st.sidebar.info(
    """
    1. Export your WhatsApp chat as a .txt file (without media).
    2. Upload the file here.
    3. Select a user (or 'Overall') from the dropdown.
    4. Click 'Show Analysis'.
    """
)

uploaded_file = st.sidebar.file_uploader("Upload a WhatsApp chat file (.txt)")

# --- Main App Title ---
st.title("💬 WhatsApp Chat Analyzer")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        st.error("File Decoding Error: Please upload a valid UTF-8 encoded text file.")
        st.stop() # Stop execution

    try:
        df = preprocessor.preprocess(data)
    except Exception as e:
        st.error(f"Error: Could not parse the file. Please make sure it's a valid WhatsApp chat log.")
        st.stop() # Stop execution

    if df.empty:
        st.warning("The uploaded file is empty or contains no recognized messages.")
        st.stop()

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
        
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if st.sidebar.button("Show Analysis"):

        # --- Top Statistics Area (Using st.metric) ---
        try:
            num_messages, words, links = helper.fetch_stats(selected_user, df)
            
            st.header(f"Top Statistics for {selected_user}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Messages", num_messages)
            with col2:
                st.metric("Total Words", words)
            with col3:
                st.metric("Links Shared", links)
        except Exception as e:
            st.error(f"Could not generate Top Statistics. Error: {e}")
        
        st.divider()

        # --- Organize all analysis into Tabs ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Activity Analysis", 
            "🧑‍🤝‍🧑 User Analysis", 
            "☁️ Word & Emoji Analysis",
            "🗓️ Raw Data"
        ])

        with tab1:
            st.subheader("Message Timelines")
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Monthly Timeline")
                monthly_timeline = helper.monthly_timeline(selected_user, df)
                if not monthly_timeline.empty:
                    fig = px.line(monthly_timeline, x='time_label', y='message', 
                                    title="Messages per Month",
                                    labels={'time_label': 'Month-Year', 'message': 'Total Messages'})
                    fig.update_layout(xaxis_title="Month-Year", yaxis_title="Total Messages")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available to display the Monthly Timeline.")

            with col2:
                st.caption("Daily Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                if not daily_timeline.empty:
                    fig = px.line(daily_timeline, x='only_date', y='message', 
                                    title="Messages per Day",
                                    labels={'only_date': 'Date', 'message': 'Total Messages'})
                    fig.update_layout(xaxis_title="Date", yaxis_title="Total Messages")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available to display the Daily Timeline.")
            
            st.divider()
            st.subheader("Activity Maps")
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, df)
                if not busy_day.empty:
                    fig = px.bar(busy_day, x=busy_day.index, y=busy_day.values,
                                   title="Activity by Day",
                                   labels={'index': 'Day of Week', 'value': 'Total Messages'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available for Most Busy Day.")

            with col2:
                st.caption("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                if not busy_month.empty:
                    fig = px.bar(busy_month, x=busy_month.index, y=busy_month.values,
                                   title="Activity by Month",
                                   labels={'index': 'Month', 'value': 'Total Messages'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available for Most Busy Month.")

            st.divider()
            st.subheader("Weekly Activity Heatmap")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if not user_heatmap.empty:
                fig = px.imshow(user_heatmap,
                                x=user_heatmap.columns,
                                y=user_heatmap.index,
                                labels=dict(x="Time Period", y="Day of Week", color="Messages"),
                                title="Weekly Activity",
                                color_continuous_scale="Viridis")
                
                fig.update_xaxes(type='category') 
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available to display the Weekly Activity Map.")
        
        with tab2:
            if selected_user == 'Overall':
                st.subheader("Most Busy Users")
                x, new_df = helper.most_busy_users(df)
                if not x.empty and not new_df.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.bar(x, x=x.index, y=x.values, 
                                       title="Top 5 Busiest Users",
                                       labels={'index': 'User', 'value': 'Total Messages'})
                        st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        st.caption("Percentage of Overall Chats")
                        st.dataframe(new_df, use_container_width=True)
                else:
                    st.info("No data available to display Most Busy Users.")
            else:
                # Replaced the simple st.info with a clearer explanation
                st.subheader("User Comparison Tab")
                st.markdown(
                    f"""
                    This tab is for comparing activity between **all users**.
                    
                    You have selected **{selected_user}**. 
                    
                    All other tabs (📈 Activity, ☁️ Word & Emoji, etc.) are already filtered to show analysis just for this user. 
                    
                    To see the 'Most Busy Users' comparison, please select **'Overall'** from the sidebar dropdown.
                    """
                )

        with tab3:
            st.subheader("Word and Emoji Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("WordCloud")
                try:
                    df_wc = helper.create_wordcloud(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.imshow(df_wc)
                    ax.axis('off')
                    st.pyplot(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not generate WordCloud. Error: {e}")

                st.divider()
                st.caption("Most Common Words")
                most_common_df = helper.most_common_words(selected_user, df)
                if not most_common_df.empty:
                    # The line `most_common_df.columns = ['Word', 'Count']` was removed
                    # because it's now done in helper.py
                    fig = px.bar(most_common_df, x='Count', y='Word', orientation='h', 
                                   title="Top 15 Most Common Words",
                                   labels={'Word': 'Word', 'Count': 'Count'})
                    fig.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No common words found (after filtering stop words and media).")
            
            with col2:
                st.caption("Emoji Analysis")
                emoji_df = helper.emoji_helper(selected_user, df)
                if not emoji_df.empty:
                    fig = px.bar(emoji_df.head(10), x='Emoji', y='Count', 
                                   title="Top 10 Emojis",
                                   labels={'Emoji': 'Emoji', 'Count': 'Count'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.divider()
                    st.caption("Emoji Count Dataframe")
                    st.dataframe(emoji_df, use_container_width=True)
                else:
                    st.info("No emojis found in the selected chat.")
                    
        with tab4:
            st.subheader("Raw Chat Data (Parsed)")
            with st.expander("Click to see Raw Dataframe"):
                st.dataframe(df, use_container_width=True)
            
else:
    st.info("Welcome to the WhatsApp Chat Analyzer! Please upload your chat file from the sidebar to begin.")
    
    with st.expander("How to Export Your WhatsApp Chat File"):
        st.markdown(
            """
            1.  **Open WhatsApp** on your phone.
            2.  Go to the **individual or group chat** you want to export.
            3.  Tap the **three-dots menu (⋮)** in the top-right corner.
            4.  Tap **More**.
            5.  Tap **Export chat**.
            6.  **IMPORTANT:** Choose **"Without Media"**. This will create a `.txt` file.
            7.  Save the `.txt` file to your computer (e.g., by emailing it to yourself) and upload it here.
            """
        )