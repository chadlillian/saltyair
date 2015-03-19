shinyUI(
  pageWithSidebar(
    headerPanel('Iris k-means clustering'),
    sidebarPanel(
      selectInput('xcol', 'X Variable', names(qq)),
      selectInput('ycol', 'Y Variable', names(qq),selected=names(iris)[[2]]),
      numericInput('clusters', 'Cluster count', 3,min = 1, max = 9)
    ),
  mainPanel(
    plotOutput('plot1')
  )
))