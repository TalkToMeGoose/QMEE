# Load required libraries
library(ggplot2)
library(dplyr)

# Function to visualize treatment effects
visualize_treatment_effects <- function(data) {
  ggplot(data, aes(x = treatment, y = node_reached)) +
    geom_boxplot() +
    theme_minimal() +
    labs(title = "Node Reached by Treatment", x = "Treatment", y = "Node Reached")
}

# Function to visualize learning effects
visualize_learning_effects <- function(data) {
  data %>%
    group_by(round) %>%
    summarise(avg_node = mean(node_reached)) %>%
    ggplot(aes(x = round, y = avg_node)) +
    geom_line() +
    geom_point() +
    theme_minimal() +
    labs(title = "Average Node Reached Over Rounds", x = "Round", y = "Average Node Reached")
}

# Function to visualize survey correlations
visualize_survey_correlations <- function(data) {
  survey_data <- data[c("altruism", "trust", "risk_tolerance", "greed", "desire_to_win")]
  cor_matrix <- cor(survey_data, use = "complete.obs")
  
  ggplot(data = reshape2::melt(cor_matrix)) +
    geom_tile(aes(x = Var1, y = Var2, fill = value)) +
    scale_fill_gradient2(low = "blue", high = "red", mid = "white", midpoint = 0) +
    theme_minimal() +
    labs(title = "Correlation Matrix of Survey Responses")
}

# Main visualization function
create_visualizations <- function(data, results) {
  treatment_plot <- visualize_treatment_effects(data)
  learning_plot <- visualize_learning_effects(data)
  survey_cor_plot <- visualize_survey_correlations(data)
  
  list(
    treatment_plot = treatment_plot,
    learning_plot = learning_plot,
    survey_cor_plot = survey_cor_plot
  )
}

# If this script is run directly, load the data, run the analysis, and create visualizations
if (sys.nframe() == 0) {
  source("scripts/data_processing.R")
  source("scripts/analysis_functions.R")
  data <- main()  # From data_processing.R
  results <- run_analysis(data)
  plots <- create_visualizations(data, results)
  
  # Display plots
  print(plots$treatment_plot)
  print(plots$learning_plot)
  print(plots$survey_cor_plot)
}