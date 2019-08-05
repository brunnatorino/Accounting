sns.set(style="whitegrid")

        # Initialize the matplotlib figure
        f, ax = plt.subplots(figsize=(6, 15))

        # Plot the total crashes
        sns.set_color_codes("pastel")
        sns.barplot(x="Value", y="Asset Class", data=dfA,
                    label="Total Value", color="b")

        # Plot the crashes where alcohol was involved
        sns.set_color_codes("muted")
        sns.barplot(x="Depreciated_Amount", y="Asset Class", data=dfA,
                    label="Depreciated", color="b")

        # Add a legend and informative axis label
        ax.legend(ncol=2, loc="lower right", frameon=True)
        ax.set(xlim=(0, 24), ylabel="",
               xlabel="Depreciated amount vs. Total Value")
        sns.despine(left=True, bottom=True)

        f.savefig('new.png')
