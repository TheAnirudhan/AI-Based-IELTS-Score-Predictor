import matplotlib.pyplot as plt

def save_score_plot(filename, value):

    plot_dir="static/"
    print(value)
    # Calculate the percentage of the value on a scale of 10
    percentage = (value / 9) * 100
    # Calculate the percentage of the remaining value
    remaining_percentage = 100 - percentage
    # Define the labels for the pie chart
    labels = ['{}%'.format(percentage), '{}%'.format(remaining_percentage)]
    # Define the sizes for each slice of the pie chart
    sizes = [percentage, remaining_percentage]
    # Define the colors for each slice of the pie chart
    colors = ['tab:blue', 'tab:gray']
    # Create the pie chart
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, colors=colors, labels=None, startangle=90)
    # Draw circle
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.patch.set_alpha(0.0)
    fig.gca().add_artist(centre_circle)
    plt.text(0, 0, f'{value}', fontsize=50, ha='center')
    # Set aspect ratio to be equal so that pie is drawn as a circle
    ax1.axis('equal')  
    # Show the pie chart
    plt.savefig(plot_dir+filename+'.png',transparent=True)