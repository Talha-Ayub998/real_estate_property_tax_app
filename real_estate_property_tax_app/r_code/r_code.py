r_code = """
perform_analysis <- function(atr_calc, values) {
  # Combine the two datasets into a single dataset
  merged_data <- atr_calc
  merged_data$v1 <- as.numeric(as.character(merged_data$v1))
  merged_data$v2 <- as.numeric(as.character(merged_data$v2))
  merged_data$v3 <- as.numeric(as.character(merged_data$v3))
  merged_data$prop_val <- as.numeric(as.character(merged_data$prop_val))
  merged_data$group_type <- as.numeric(as.character(merged_data$group_type))
  merged_data$atr <- as.numeric(as.character(merged_data$atr))
  
  
  # Calculate the average atr for each value_bin when group_type is 1
  average_atr <- with(merged_data, tapply(atr[group_type == 1], value_bin[group_type == 1], mean))
  
  # Replace atr values where atr is 0 and group_type is 1 with the average atr for the same value_bin
  merged_data$atr[merged_data$atr == 0 & merged_data$group_type == 1] <- with(merged_data, average_atr[value_bin[atr == 0 & group_type == 1]])
  
  # Check if all values within a value_bin are 0 and drop those observations
  to_drop <- with(merged_data, tapply(atr, value_bin, function(x) all(x == 0)))
  merged_data <- merged_data[!(merged_data$value_bin %in% names(to_drop) & to_drop[as.character(merged_data$value_bin)]), ]
  
  # Check if the total number of observations for group_type == 1 is less than 12
  #  if (sum(merged_data$group_type == 1) < 12) {
  #    message("We can't proceed further. Thanks.")
  #  } else {
  #    # Ensure that the result is numeric
  #    merged_data$atr <- as.numeric(as.character(merged_data$atr))
  #    # Continue with further processing if needed
  #  }
  
  df <- merged_data
  df$lprop_val <- log(df$prop_val)
  
  # knots:
  k1 <- df %>%
    subset(v2 != 0 & v3 == 0) %>%
    mutate(k1val = lprop_val - v2)
  k1 <- mean(k1$k1val)
  k2 <- df %>%
    subset(v3 != 0) %>%
    mutate(k2val = lprop_val - v3)
  k2 <- mean(k2$k2val)
  vmin <- 12
  vmax <- 21
  
  df <- df %>%
    mutate(atr=atr/100)

    # get the spline that goes below zero as a reference.
    cspline <- lm(atr ~ v1 + v2 + v3,
                data = subset(df, group_type == 1))
    df$atrh_cspline <- predict.lm(cspline, df)
    
    # Use restriktor and apply the 8 restrictions
    ## specify the restriction matrix. Restriktor wants it in the form R * \theta >= rhs
    myConstraints <- rbind(c(1, vmin, 0, 0),                     # 1. above 0 at vmin
                        c(-1, -vmin, 0, 0),                   # 2. below 100 at vmin
                        c(1, k1, 0, 0),                       # 3. above 0 at k1
                        c(-1, -k1, 0, 0),                     # 4. below 100 at k1
                        c(1, k1, (k2 - k1), 0),               # 5. above 0 at k2
                        c(-1, -k1, -(k2 - k1), 0),            # 6. below 100 at k2
                        c(1, k1, (k2 - k1), (vmax - k2)),     # 7. above 0 at vmax
                        c(-1, -k1, -(k2 - k1), -(vmax - k2))) # 8. below 100 at vmax
    
    myRhs <- c(0, -100, 0, -100, 0, -100, 0, -100)
    
    ## run the restricted regression
    # Measure the time before some operation
    ptm <- proc.time()
    restr.cspline <- restriktor(cspline, 
                                constraints = myConstraints,
                                rhs = myRhs,
                                mix.weights = "boot",
                                se = "none")
    plot_data <- data.frame(prop_val = df$prop_val, 
                          prediction = df$atrh_cspline,
                          pred=df$atrh_cspline,
                          atr=df$atr, 
                          group_type=df$group_type,
                          onlyuse=df$onlyuse,
                          onlyocc=df$onlyocc)
  
  # Create the theta variable
  plot_data <- plot_data %>% 
    mutate(theta = ifelse(group_type == 1, 1, atr / pred))
  
  # Identify rows with group_type == 1, onlyuse is either "Commercial" or "Residential", and onlyocc is either "Self-occupied" or "Rented"
  replace_condition <- plot_data$group_type == 1 & plot_data$onlyuse %in% c("Commercial") & plot_data$onlyocc %in% c("Self-occupied")
  
  # Replace theta for corresponding conditions in group_type == 0
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- 0.25
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- as.numeric(1.25)
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- 1
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- 5
  }
  
  # Identify rows with group_type == 1, onlyuse is either "Commercial" or "Residential", and onlyocc is either "Self-occupied" or "Rented"
  replace_condition <- plot_data$group_type == 1 & plot_data$onlyuse %in% c("Residential") & plot_data$onlyocc %in% c("Self-occupied")
  
  # Replace theta for corresponding conditions in group_type == 0
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- as.numeric(1)
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- 5
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- 4
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- 20
  }
  
  # Identify rows with group_type == 1, onlyuse is either "Commercial" or "Residential", and onlyocc is either "Self-occupied" or "Rented"
  replace_condition <- plot_data$group_type == 1 & plot_data$onlyuse %in% c("Residential") & plot_data$onlyocc %in% c("Rented")
  
  # Replace theta for corresponding conditions in group_type == 0
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- 0.2
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- 1
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- 0.8
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- 4
  }
  
  # Identify rows with group_type == 1, onlyuse is either "Commercial" or "Residential", and onlyocc is either "Self-occupied" or "Rented"
  replace_condition <- plot_data$group_type == 1 & plot_data$onlyuse %in% c("Commercial") & plot_data$onlyocc %in% c("Rented")
  
  # Replace theta for corresponding conditions in group_type == 0
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- 0.05
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Residential" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- 0.25
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Self-occupied" & plot_data$theta == 0] <- 0.2
  }
  
  if (any(replace_condition)) {
    plot_data$theta[plot_data$group_type == 0 & plot_data$onlyuse == "Commercial" & plot_data$onlyocc == "Rented" & plot_data$theta == 0] <- 1
  }
  
  
  # Print linear regression summary
  summary(restr.cspline)
  
  # Print the summary
  summary_info <-   summary(restr.cspline)
  
  
  
  # Extract coefficients
  coefficients <- coef(summary_info)
  beta0 <- coefficients[1]  # Intercept
  beta1 <- coefficients[2] 
  beta2 <- coefficients[3]
  beta3 <- coefficients[4] 
  
  
  # Split the data into two datasets
  group_1_data <- plot_data %>% filter(group_type == 1) %>% slice_head(n = 1)
  group_0_data <- plot_data %>% filter(group_type == 0)
  
  # Append or concatenate group_1_data and group_0_data
  combined_data <- bind_rows(group_1_data, group_0_data)
  
  
  selected_data <- combined_data %>%
    select(theta, group_type, onlyocc, onlyuse)%>%
    mutate(beta0 = beta0,
           beta1 = beta1,
           beta2 = beta2,
           beta3 = beta3)
  
  final_data <- merge(selected_data, values, by = c("onlyuse", "onlyocc"), all.x = TRUE)
  
  final_data <- final_data %>%
    mutate(
      rr_1 = beta0 * v_1 + beta1 * v_v1_1 + beta2 * v_v2_1 + beta3 * v_v3_1,
      rr_2 = beta0 * v_2 + beta1 * v_v1_2 + beta2 * v_v2_2 + beta3 * v_v3_2,
      rr_3 = beta0 * v_3 + beta1 * v_v1_3 + beta2 * v_v2_3 + beta3 * v_v3_3,
      rr_4 = beta0 * v_4 + beta1 * v_v1_4 + beta2 * v_v2_4 + beta3 * v_v3_4
    ) 
  
  rr_values_group_1 <- final_data %>%
    filter(group_type == 1) %>%
    select(rr_1, rr_2, rr_3, rr_4)
  
  sub_data <- final_data %>%
    select(theta, onlyocc, onlyuse, group_type, group)
  
  rr_values_long <- rr_values_group_1 %>%
    gather(key = "group", value = "rr_value", rr_1:rr_4) %>%
    mutate(group = as.numeric(sub("rr_", "", group)))
  
  revenue <- merge(rr_values_long, sub_data, by = "group") %>%
    mutate(revenue = rr_value * theta)
  
  total_revenue <- revenue %>%
    summarise(total_revenue = sum(revenue)) %>%
    mutate(total_revenue = (total_revenue * 1.741784)/1e9) %>%
    mutate(current_revenue = 5.45) %>%
    mutate(gap = total_revenue - current_revenue)
  
  revenues_long <- tidyr::gather(total_revenue, key = "Revenue_Type", value = "Revenue", current_revenue, total_revenue)
  # Divide values in the "Revenue" column by a billion
  # Create a bar chart using ggplot
  # Set custom labels for x-axis variables
  labels <- c("current_revenue" = "Revenue raised \n FY22", "total_revenue" = "Revenue raised from your \npreferred schedule")
  revenues_long$Revenue_Type_Label <- labels[revenues_long$Revenue_Type]

  
  return(total_revenue)
  print("code_chunk_4")
}
"""