# Whatsapp-chat-analyzer-streamlit

<p>This project demonstrates the power of data analysis and visualization by transforming unstructured WhatsApp chat exports into meaningful insights. Built with Python and Streamlit, this interactive web application parses chat files, processes the text data using Pandas, and generates insightful visualizations with Plotly, Matplotlib and Seaborn.

The analyzer extracts key statistics, visualizes communication patterns over time (monthly, daily, weekly), identifies the most active users and busiest periods, performs text analysis to find common words and emojis, and presents this information in an easy-to-understand dashboard. It's designed to handle various export formats (Android/iOS, 12/24-hour) robustly, showcasing data cleaning and processing skills essential for any analyst.</p>

<h2>Features</h2>

<ul>
    <li><strong>Message Statistics:</strong> Get an overview of your chat, including the total number of messages, words, and links shared.</li>
    <li><strong>Monthly Timeline:</strong> Visualize your chat activity over months to identify trends and patterns.</li>
    <li><strong>Daily Timeline:</strong> View your daily chat activity to pinpoint specific active days.</li>
    <li><strong>Activity Map:</strong> Explore your busiest days and months, helping you understand your chat behavior.</li>
    <li><strong>WordCloud:</strong> Visualize the most frequently used words in your chats.</li>
    <li><strong>Most Common Words:</strong> Identify and analyze the most commonly used words.</li>
    <li><strong>Emoji Analysis:</strong> Understand emoji usage patterns and frequencies.</li>
    <li><strong>Group Level Insights:</strong> If analyzing a group chat, discover the most active participants and their message contributions.</li>
</ul>

<h2>How to Use</h2>

<ol>
    <li>Upload your WhatsApp chat file (exported `.txt` file).</li>
    <li>Select a specific user (participant) for individual analysis or choose "Overall" for an overview.</li>
    <li>Click the "Show Analysis" button to generate insights and visualizations.</li>
</ol>

<h2>Getting Started</h2>

<p>To run this application locally, follow these steps:</p>

<ol>
    <li>Clone the repository to your local machine:</li>
</ol>

<pre>
<code>git clone https://github.com/your-username/whatsapp-chat-analyzer.git
cd whatsapp-chat-analyzer</code>
</pre>

<ol start="2">
    <li>Install the required Python packages:</li>
</ol>

<pre>
<code>pip install streamlit matplotlib seaborn</code>
</pre>

<ol start="3">
    <li>Run the application:</li>
</ol>

<pre>
<code>streamlit run whatsapp_analyzer.py</code>
</pre>

<h2>Customization</h2>

<p>You can customize this application by modifying the code to include additional features or visualizations to suit your chat analysis needs.</p>

<p>Unlock the insights hidden within your WhatsApp chats with the WhatsApp Chat Analyzer!</p>
