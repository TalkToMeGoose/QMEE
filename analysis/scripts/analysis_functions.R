# Load required libraries
library(tidyverse)
library(lme4)
library(emmeans)
library(car)
library(gridExtra)  # For arranging multiple plots

# Function to check normality
test_normality <- function(data) {
  
  # Q-Q plot
  qq_plot <- ggplot(data, aes(sample = node_reached)) +
    stat_qq() +
    stat_qq_line() +
    theme_minimal() +
    labs(title = "Q-Q Plot of Node Reached")
  
  # Histogram
  hist_plot <- ggplot(data, aes(x = node_reached)) +
    geom_histogram(binwidth = 1, fill = "blue", alpha = 0.7) +
    theme_minimal() +
    labs(title = "Histogram of Node Reached", x = "Node Reached", y = "Frequency")
  
  list(qq_plot = qq_plot, hist_plot = hist_plot)
}

# Function to check residual normality
check_residual_normality <- function(model) {
  residuals <- resid(model)
  shapiro_test <- shapiro.test(residuals)
  
  qq__residual_plot <- ggplot(data.frame(residuals), aes(sample = residuals)) +
    stat_qq() +
    stat_qq_line() +
    theme_minimal() +
    labs(title = "Q-Q Plot of Model Residuals")
  
  list(shapiro_test = shapiro_test, qq_residual_plot = qq_residual_plot)
}

# Function to test for treatment effects
test_treatment_effects <- function(data) {
  # Mixed-effects model
  model <- lmer(node_reached ~ treatment + (1|participant_id) + (1|group_id), data = data)
  
  # ANOVA-like table for fixed effects
  anova_results <- Anova(model)
  
  # Pairwise comparisons
  emm <- emmeans(model, ~ treatment)
  pairwise_comparisons <- pairs(emm)
  residual_normality <- check_residual_normality(model)
  
  list(model = model, anova = anova_results, pairwise = pairwise_comparisons, 
       residual_normality = residual_normality)
}

# Function to test for order effects
test_order_effects <- function(data) {
  model <- lmer(node_reached ~ treatment * round + (1|participant_id) + (1|group_id), data = data)
  anova_results <- Anova(model)
  residual_normality <- check_residual_normality(model)
  
  list(model = model, anova = anova_results, residual_normality = residual_normality)
}

# Function to test for learning effects
test_learning_effects <- function(data) {
  model <- lmer(node_reached ~ round + (1|participant_id) + (1|group_id), data = data)
  anova_results <- Anova(model)
  residual_normality <- check_residual_normality(model)
  
  list(model = model, anova = anova_results, residual_normality = residual_normality)
}

# Function to analyze survey responses
analyze_survey_responses <- function(data) {
  survey_vars <- c("altruism", "trust", "risk_tolerance", "greed", "desire_to_win")
  
  # Pearson correlations
  pearson_cor <- cor(data[survey_vars], use = "complete.obs", method = "pearson")
  
  # Relationship between survey responses and game behavior
  behavior_model <- lmer(node_reached ~ altruism + trust + risk_tolerance + greed + desire_to_win + 
                           (1|participant_id) + (1|group_id), data = data)
  behavior_model_summary <- summary(behavior_model)
  residual_normality <- check_residual_normality(behavior_model)
  
  list(pearson_cor = pearson_cor, behavior_model = behavior_model_summary, 
       residual_normality = residual_normality)
}

# Function to save or display plots
save_or_display_plots <- function(plot_list, filename = NULL) {
  if (!is.null(filename)) {
    # Save to file
    ggsave(filename, 
           plot = do.call(grid.arrange, c(plot_list, ncol = 2)),
           width = 12, height = 6 * ceiling(length(plot_list) / 2))
    cat("Plots saved to", filename, "\n")
  } else {
    # Display in R graphics device
    do.call(grid.arrange, c(plot_list, ncol = 2))
  }
}

# Main analysis function
run_analysis <- function(data, save_plots = FALSE) {
  treatment_effects <- test_treatment_effects(data)
  order_effects <- test_order_effects(data)
  learning_effects <- test_learning_effects(data)
  survey_analysis <- analyze_survey_responses(data)
  
  # Collect all Q-Q plots
  qq_plots <- list(
    treatment_effects$residual_normality$qq_plot,
    order_effects$residual_normality$qq_plot,
    learning_effects$residual_normality$qq_plot,
    survey_analysis$residual_normality$qq_plot
  )
  
  # Save or display Q-Q plots
  if (save_plots) {
    save_or_display_plots(qq_plots, "qq_plots.png")
  } else {
    save_or_display_plots(qq_plots)
  }
  
  list(
    treatment_effects = treatment_effects,
    order_effects = order_effects,
    learning_effects = learning_effects,
    survey_analysis = survey_analysis
  )
}

# If this script is run directly, load the data and run the analysis
if (sys.nframe() == 0) {
  source("scripts/data_processing.R")
  data <- main()  # From data_processing.R
  results <- run_analysis(data, save_plots = TRUE)
  print(str(results))  # Print the structure of the results
}
