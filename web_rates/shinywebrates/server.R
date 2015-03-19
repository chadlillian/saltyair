palette(c("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3",
          "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999"))

qq<-read.table("cleanrates.csv")

shinyServer(function(input, output, session) 
  {
  # Combine the selected variables into a new data frame
  
#  selectedData <- reactive({iris[, c(input$xcol, input$ycol)]})
  
  clusters <- reactive({kmeans(qq, input$clusters)})
  qqq<-reactive({data.frame(qq,clusters$cluster)})
  #output$plot1<-renderPlot(qplot(qq$row.names, qq$input$xcol)) #,color=qqq$clusters.cluster)})
  qplot(qq$row.names, qq$input$xcol)
  
#    renderPlot({par(mar = c(5.1, 4.1, 0, 1))
#   plot(selectedData(),col = clusters()$cluster,pch = 20, cex = 3)
#    points(clusters()$centers, pch = 4, cex = 4, lwd = 4)
#  })
  
})