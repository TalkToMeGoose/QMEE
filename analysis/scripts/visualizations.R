# Load required libraries
library(ggplot2)
library(dplyr)

# Function to visualize treatment effects
visualize_treatment_effects <- function(data) {
  plot <- ggplot(data, aes(x = treatment, y = node_reached)) +
    geom_boxplot() +
    theme_minimal() +
    labs(title = "Node Reached by Treatment", x = "Treatment", y = "Node Reached")  
  return(plot)
}

# Function to visualize learning effects
visualize_learning_effects <- function(data) {
  plot <- data %>%
    group_by(round) %>%
    summarise(avg_node = mean(node_reached)) %>%
    ggplot(aes(x = round, y = avg_node)) +
    geom_line() +
    geom_point() +
    theme_minimal() +
    labs(title = "Average Node Reached Over Rounds", x = "Round", y = "Average Node Reached")
  
  return(plot)
}

# Function to visualize survey correlations
visualize_survey_correlations <- function(data) {
  survey_data <- data[c("altruism", "trust", "risk_tolerance", "greed", "desire_to_win")]
  cor_matrix <- cor(survey_data, use = "complete.obs")
  
  plot <- ggplot(data = reshape2::melt(cor_matrix)) +
    geom_tile(aes(x = Var1, y = Var2, fill = value)) +
    scale_fill_gradient2(low = "blue", high = "red", mid = "white", midpoint = 0) +
    theme_minimal() +
    labs(title = "Correlation Matrix of Survey Responses")
  
  return(plot)
}

# Function to display or save a single plot
display_or_save_plot <- function(plot, filename = NULL) {
  if (!is.null(filename)) {
    ggsave(filename, plot = plot, width = 10, height = 6)
    cat("Plot saved to", filename, "\n")
  } else {
    print(plot)
  }
}

# Main visualization function
create_visualizations <- function(data, save_plots = FALSE) {
  treatment_plot <- visualize_treatment_effects(data)
  learning_plot <- visualize_learning_effects(data)
  survey_cor_plot <- visualize_survey_correlations(data)
  
  if (save_plots) {
    display_or_save_plot(treatment_plot, "treatment_effects.png")
    display_or_save_plot(learning_plot, "learning_effects.png")
    display_or_save_plot(survey_cor_plot, "survey_correlations.png")
  } else {
    display_or_save_plot(treatment_plot)
    display_or_save_plot(learning_plot)
    display_or_save_plot(survey_cor_plot)
  }
  
  list(
    treatment_plot = treatment_plot,
    learning_plot = learning_plot,
    survey_cor_plot = survey_cor_plot
  )
}

# If this script is run directly, load the data and create visualizations
if (sys.nframe() == 0) {
  source("scripts/data_processing.R")
  data <- main()  # From data_processing.R
  plots <- create_visualizations(data, save_plots = FALSE)
}
