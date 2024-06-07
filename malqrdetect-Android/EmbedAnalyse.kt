package com.example.malqrdetect

import android.content.Intent
import android.content.res.AssetFileDescriptor
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.AnimatedVisibilityScope
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.layout.wrapContentSize
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.material.ButtonDefaults
import androidx.compose.material.CircularProgressIndicator
import androidx.compose.material.Icon
import androidx.compose.material.IconButton
import androidx.compose.material.MaterialTheme
import androidx.compose.material.ProgressIndicatorDefaults
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.example.malqrdetect.ui.theme.EmbedAnalyseTheme
import com.google.accompanist.pager.ExperimentalPagerApi
import com.google.accompanist.pager.HorizontalPager
import com.google.accompanist.pager.rememberPagerState
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.math.sqrt


class EmbedAnalyse : ComponentActivity(), CoroutineScope by MainScope() {

    //Global variables for the app

    //Greeting text is the value from the model (kept in as a little nod to the first version of the app)
    private val greetingText = mutableStateOf<String?>(null)
    private val progressValue = mutableStateOf(0.0f)
    private val updateText = mutableStateOf<String?>("Initialising...")
    private val embeddedURL = mutableStateOf<String?>(null)
    private val rates = mutableStateOf<Array<*>?>(null)
    private val holdOutputMessage = mutableStateOf<Int?>(null)
    private val holdFixedURL = mutableStateOf<String?>(null)

    private var greenRectangleVisible by mutableStateOf(false)
    private var yellowRectangleVisible by mutableStateOf(false)
    private var redRectangleVisible by mutableStateOf(false)





    //Activate the main function
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            EmbedAnalyseTheme {
                MainContent()
            }
        }
    }

    //Mission control function for overarching UI and user interaction
    @Composable
    private fun MainContent() {
        // A surface container using the 'background' color from the theme
        Surface(
            modifier = Modifier.fillMaxSize()
        ) {

            //Check if the prediction has finished
            if(progressValue.value == 1.0f)
            {
                //If so, display the indicator buttons
                IndicatorButtons()

                //Display the bottom buttons
                BottomButtons()

            }

            //Display the progress bar and the text
            ProgressBarRootView(progress = progressValue.value,update = updateText.value ?: "", embeddedURL.value ?: "",greetingText.value ?: "",rates = rates.value,holdOutputMessage.value,holdFixedURL.value)

            //Get the tflite model in the app
            GetTfliteModel()


        }



    }

    //Display the back and view URL buttons at the bottom of the screen
    @Composable
    private fun BottomButtons(){
        // Define the state for the offset
        var offsetState by remember { mutableStateOf(100.dp) }

        var openURL by remember { mutableStateOf(false) }

        var textVisibility by remember { mutableStateOf(false) }

        //Animation hold
        LaunchedEffect(true) {
            delay(1500)
            offsetState = 0.dp
            //Make the text visible after the buttons appear
            delay(1000)
            textVisibility = true
        }

        Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Bottom) {

            AnimatedVisibility(visible = textVisibility, enter = fadeIn(), exit = fadeOut()) {
                Text(
                    text = "Tap each ring to learn more!",
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.h6
                )
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {

                // Animate the offset of the boxes and the time the animation plays out
                val offsetY by animateDpAsState(targetValue = offsetState,animationSpec = tween(durationMillis = 750))

                Box(
                    modifier = Modifier
                        .weight(0.3f)
                        .aspectRatio(2f)
                        .fillMaxWidth(0.5f)
                        .offset(y = offsetY)
                        .clip(RoundedCornerShape(50.dp))// apply the animated offset
                        .background(Color(android.graphics.Color.parseColor("#9900ef")))
                        .clickable { finish() },
                    contentAlignment = Alignment.Center
                ) {
                    Text("Back", color = Color.White)
                }

                Spacer(modifier =Modifier.width(10.dp))

                Box(
                    modifier = Modifier
                        .weight(0.3f)
                        .aspectRatio(2f)
                        .fillMaxWidth(0.5f)
                        .offset(y = offsetY)
                        .clip(RoundedCornerShape(50.dp))
                        .background(Color(android.graphics.Color.parseColor("#9900ef")))
                        .clickable { openURL = true },
                    contentAlignment = Alignment.Center
                ) {
                    Text("View Content", color = Color.White)
                }
            }
        }

        // Display the entire URL in a dialog box
        if(openURL)
        {
            AnimatedTransitionDialog(
                onDismissRequest = { openURL = false },
                contentAlignment = Alignment.Center,
                content = { dialogHelper ->
                    Surface(
                        shape = RoundedCornerShape(16.dp),
                        color = Color(0x99, 0x00, 0xEF)
                    ) {
                        Box(
                            modifier = Modifier
                                .padding(8.dp)
                                .background(Color(0x99, 0x00, 0xEF))
                                .wrapContentSize()
                        ) {
                            Column(
                                modifier = Modifier
                                    .padding(8.dp)
                                    //.verticalScroll(rememberScrollState()) //Adding this changes the colour of large amounts of text to grey.
                            ) {
                                Text(
                                    text = embeddedURL.value.toString(),
                                    style = MaterialTheme.typography.body1,
                                    modifier = Modifier.padding(40.dp),
                                    color = Color.White
                                )
                            }
                            // Close Button
                            IconButton(
                                onClick = { dialogHelper.triggerAnimatedDismiss() },
                                modifier = Modifier
                                    .align(Alignment.TopEnd)
                                    .padding(8.dp)
                            ) {
                                Icon(Icons.Default.Close, contentDescription = "Close")
                            }
                        }
                    }
                }
            )
        }
    }

    //Function to display the scoring system to the user at the top of the page
    @Composable
    private fun IndicatorButtons() {
        Box(modifier = Modifier
            .fillMaxWidth()
            .padding(10.dp))
        {
            val canvasModifier = Modifier
                .fillMaxWidth()
                .fillMaxHeight(0.05f)

            //Define the original state of the rectangles so that they are offscreen to begin with and come down onto the screen
            val offScreenOffset = (-300).dp
            val onScreenOffset = 0.dp

            //Set the visibility of the line from the rectangle to false
            val finalLength = 50f
            var lineVisible by remember { mutableStateOf(false) }
            val animatedLength by animateFloatAsState(if (lineVisible) finalLength else 0f)

            //Animate the rectangle popup on screen
            var rectangleVisible by remember { mutableStateOf(false) }
            val animatedRectangle by animateFloatAsState(if (rectangleVisible) 1f else 0f)

            //Variables to hold the state of the rectangles
            var greenRectClicked by remember { mutableStateOf(false) }
            var yellowRectClicked by remember { mutableStateOf(false) }
            var redRectClicked by remember { mutableStateOf(false) }
            var externalRectangleClicked = remember { mutableStateOf(false) }

            var rectSectionWidth  by remember { mutableStateOf(0f) }
            var rectSectionHeight by remember { mutableStateOf(0f) }




            //Hold the animated state for each rectangle
            val greenOffset by animateDpAsState(if (greenRectangleVisible) onScreenOffset else offScreenOffset)
            val yellowOffset by animateDpAsState(if (yellowRectangleVisible) onScreenOffset else offScreenOffset)
            val redOffset by animateDpAsState(if (redRectangleVisible) onScreenOffset else offScreenOffset)

            // Start the animations in sequence when the Canvas becomes visible
            LaunchedEffect(Unit) {
                greenRectangleVisible = true
                delay(250)
                yellowRectangleVisible = true
                delay(250)
                redRectangleVisible = true
                delay(250)
                lineVisible = true
                delay(400)
                rectangleVisible = true
            }

            val rectangleBounds = remember { mutableStateListOf<RectF>() }

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .pointerInput(Unit) {
                        detectTapGestures { offset ->
                            rectangleBounds.forEachIndexed { index, rectF ->
                                if (rectF.contains(offset.x, offset.y)) {
                                    when (index) {
                                        0 -> greenRectClicked = true
                                        1 -> yellowRectClicked = true
                                        2 -> redRectClicked = true
                                    }
                                }
                            }
                        }
                    }
            ) {
                //Draw the rectangles at the top of the screen
                val configuration = LocalConfiguration.current
                val screenWidth = configuration.screenWidthDp
                val density = LocalDensity.current.density
                Canvas(modifier = canvasModifier) {

                    val sectionWidth = size.width / 3
                    val sectionHeight = size.height

                    rectSectionHeight = (sectionHeight * 0.80).toFloat()
                    rectSectionWidth = size.width/2

                    rectangleBounds.clear()

                    val cornerRadius = CornerRadius(50f, 50f)


                    // Define the text to be drawn and the paint style
                    var text = "Benign"


                    val paint = Paint().apply {
                        color = android.graphics.Color.parseColor("#FFFFFF")
                        textSize = screenWidth / 20 * density
                    }

                    // Draw rectangles and store their bounds
                    val rect1 = RectF(0f,greenOffset.toPx(),0f + sectionWidth, greenOffset.toPx() + sectionHeight)
                    drawRoundRect(Color.Green, topLeft = Offset(rect1.left, rect1.top), size = Size(rect1.width(), rect1.height()), cornerRadius = cornerRadius)
                    rectangleBounds.add(rect1)

                    drawIntoCanvas { canvas ->
                        val textWidth = paint.measureText(text)
                        val textHeight = paint.fontMetrics.descent - paint.fontMetrics.ascent
                        val textOffsetX = (rect1.width() - textWidth) / 2
                        val textOffsetY = (rect1.height() - textHeight) / 2 - paint.fontMetrics.ascent
                        canvas.nativeCanvas.drawText(text, rect1.left + textOffsetX, rect1.top + textOffsetY, paint)
                    }

                    text = "Unknown"

                    val rect2 = RectF(sectionWidth, yellowOffset.toPx(), sectionWidth + sectionWidth, yellowOffset.toPx() + sectionHeight)
                    drawRoundRect(Color(android.graphics.Color.parseColor("#808000")), topLeft = Offset(rect2.left, rect2.top), size = Size(rect2.width(), rect2.height()), cornerRadius = cornerRadius)
                    rectangleBounds.add(rect2)

                    drawIntoCanvas { canvas ->
                        val textWidth = paint.measureText(text)
                        val textHeight = paint.fontMetrics.descent - paint.fontMetrics.ascent
                        val textOffsetX = (rect2.width() - textWidth) / 2
                        val textOffsetY = (rect2.height() - textHeight) / 2 - paint.fontMetrics.ascent
                        canvas.nativeCanvas.drawText(text, rect2.left + textOffsetX, rect2.top + textOffsetY, paint)
                    }

                    val rect3 = RectF(sectionWidth *2, redOffset.toPx(), sectionWidth * 2 + sectionWidth, redOffset.toPx() + sectionHeight)
                    drawRoundRect(Color.Red, topLeft = Offset(rect3.left, rect3.top), size = Size(rect3.width(), rect3.height()), cornerRadius = cornerRadius)
                    rectangleBounds.add(rect3)

                    text = "Malicious"

                    drawIntoCanvas { canvas ->
                        val textWidth = paint.measureText(text)
                        val textHeight = paint.fontMetrics.descent - paint.fontMetrics.ascent
                        val textOffsetX = (rect2.width() - textWidth) / 2
                        val textOffsetY = (rect2.height() - textHeight) / 2 - paint.fontMetrics.ascent
                        canvas.nativeCanvas.drawText(text, rect3.left + textOffsetX, rect3.top + textOffsetY, paint)
                    }
                }
            }

            //Clickable box for the popdown box
            Box(
                modifier = Modifier
                    .size(rectSectionWidth.dp, 50.dp)
                    .offset(x = 0.dp, y = rectSectionHeight.dp)
                    .clickable(onClick = {
                        externalRectangleClicked.value = true
                    })
                    .background(Color.Transparent)
            )

            Canvas(modifier = canvasModifier) {

                val sectionWidth = size.width / 3

                //Check where the prediction score boundaries lie to create a unique pointer to each.

                //Embedded content most likely text
                if(holdOutputMessage.value == 2)
                {

                    drawGradientLine(
                        canvas = this,
                        sectionWidth = (sectionWidth * 1.5).toFloat(),
                        startColor = Color(android.graphics.Color.parseColor("#808000")),
                        endColor = Color(android.graphics.Color.parseColor("#818148")),
                        size = size,
                        animatedLength = animatedLength
                    )
                    drawRectangleSection(
                        canvas = this,
                        size = size,
                        endColor = Color(android.graphics.Color.parseColor("#818148")),
                        rectLeft = 0f,
                        rectRight = size.width,
                        message = "Embedded content is most likely text",
                        scale = animatedRectangle
                    )

                }
                //Embedded content failed to make successful request
                else if(holdOutputMessage.value == 1)
                {
                    drawGradientLine(
                        canvas = this,
                        sectionWidth = (sectionWidth * 1.5).toFloat(),
                        startColor = Color(android.graphics.Color.parseColor("#808000")),
                        endColor = Color(android.graphics.Color.parseColor("#818148")),
                        size = size,
                        animatedLength = animatedLength
                    )
                    drawRectangleSection(
                        canvas = this,
                        size = size,
                        endColor = Color(android.graphics.Color.parseColor("#818148")),
                        rectLeft = 0f,
                        rectRight = size.width,
                        message = "Failed to make a successful request",
                        scale = animatedRectangle
                    )

                }
                //Benign
                else if(greetingText.value?.toFloat()!! < -3)
                {

                    drawGradientLine(
                        canvas = this,
                        sectionWidth = sectionWidth/2,
                        startColor = Color.Green,
                        endColor = Color(android.graphics.Color.parseColor("#4c9671")),
                        size = size,
                        animatedLength = animatedLength
                    )
                    drawRectangleSection(
                        canvas = this,
                        size = size,
                        endColor = Color(android.graphics.Color.parseColor("#4c9671")),
                        rectLeft = 0f,
                        rectRight = size.width,
                        message = "Content is most likely benign",
                        scale = animatedRectangle
                    )
                }
                //Malicious
                else if(greetingText.value?.toFloat()!! > 3)
                {

                    drawGradientLine(
                        canvas = this,
                        sectionWidth = (sectionWidth*2.5).toFloat(),
                        startColor = Color.Red,
                        endColor = Color(android.graphics.Color.parseColor("#b5542e")),
                        size = size,
                        animatedLength = animatedLength
                    )
                    drawRectangleSection(
                        canvas = this,
                        size = size,
                        endColor = Color(android.graphics.Color.parseColor("#b5542e")),
                        rectLeft = 0f,
                        rectRight = size.width,
                        message = "Content is most likely malicious",
                        scale = animatedRectangle
                    )
                }
                //Unknown
                else
                {
                    drawGradientLine(
                        canvas = this,
                        sectionWidth = (sectionWidth * 1.5).toFloat(),
                        startColor = Color(android.graphics.Color.parseColor("#808000")),
                        endColor = Color(android.graphics.Color.parseColor("#818148")),
                        size = size,
                        animatedLength = animatedLength
                    )
                    drawRectangleSection(
                        canvas = this,
                        size = size,
                        endColor = Color(android.graphics.Color.parseColor("#818148")),
                        rectLeft = 0f,
                        rectRight = size.width,
                        message = "Embedded content is unknown",
                        scale = animatedRectangle
                    )
                }
            }

            //Code to display unique messages to the user depending on the outcome of the analysis and what section is clicked
            if(greenRectClicked)
            {
                if(holdOutputMessage.value == 2)
                {
                    displayDialog(clicked = greenRectClicked, text = (greetingText.value).toString(), dialogColor = Color.Green, uniqueMessage = "The embedded content has been predicted as text"){
                        greenRectClicked = it
                    }
                }
                else if(greetingText.value?.toFloat()!! < -3)
                {
                    displayDialog(clicked = greenRectClicked, text = (greetingText.value).toString(), dialogColor = Color.Green, uniqueMessage = "The embedded content has been predicted as benign"){
                        greenRectClicked = it
                    }
                }
                else{
                    displayDialog(clicked = greenRectClicked, text = (greetingText.value).toString(), dialogColor = Color.Green, uniqueMessage = "The embedded content hasn't been predicted as benign"){
                        greenRectClicked = it
                    }
                }


            }

            if(yellowRectClicked)
            {
                if(holdOutputMessage.value == 2)
                {
                    displayDialog(clicked = greenRectClicked, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#808000")), uniqueMessage = "The embedded content has been predicted as text"){
                        greenRectClicked = it
                    }
                }
                else if(holdOutputMessage.value == 1)
                {
                    displayDialog(clicked = yellowRectClicked, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#808000")), uniqueMessage = "The embedded content failed to make a successful request"){
                        yellowRectClicked = it
                    }
                }
                else if(greetingText.value?.toFloat()!! > -3 || greetingText.value?.toFloat()!! < 3 )
                {
                    displayDialog(clicked = yellowRectClicked, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#808000")), uniqueMessage = "The embedded content has not been marked as unknown"){
                        yellowRectClicked = it
                    }
                }
                else{
                    displayDialog(clicked = yellowRectClicked, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#808000")), uniqueMessage = "The embedded content has been marked as unknown"){
                        yellowRectClicked = it
                    }
                }

            }

            if(redRectClicked)
            {
                if(holdOutputMessage.value == 2)
                {
                    displayDialog(clicked = greenRectClicked, text = (greetingText.value).toString(), dialogColor = Color.Red, uniqueMessage = "The embedded content has been predicted as text"){
                        greenRectClicked = it
                    }
                }
                else if(greetingText.value?.toFloat()!! > 3)
                {
                    displayDialog(clicked = redRectClicked, text = (greetingText.value).toString(), dialogColor = Color.Red, uniqueMessage = "The embedded content has been predicted as malicious"){
                        redRectClicked = it
                    }
                }
                else{
                    displayDialog(clicked = redRectClicked, text = (greetingText.value).toString(), dialogColor = Color.Red, uniqueMessage = "The embedded content hasn't been predicted as malicious"){
                        redRectClicked = it
                    }
                }
            }

            if(externalRectangleClicked.value)
            {
                if(holdOutputMessage.value == 2)
                {
                    displayDialog(clicked = externalRectangleClicked.value, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#818148")), uniqueMessage = "The embedded content has been predicted as text"){
                        externalRectangleClicked.value = it
                    }
                }
                else if(greetingText.value?.toFloat()!! < -3)
                {
                    displayDialog(clicked = externalRectangleClicked.value, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#4c9671")), uniqueMessage = "The embedded content has been predicted as benign"){
                        externalRectangleClicked.value = it
                    }
                }
                else if(greetingText.value?.toFloat()!! > 3)
                {
                    displayDialog(clicked = externalRectangleClicked.value, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#b5542e")), uniqueMessage = "The embedded content has been predicted as malicious"){
                        externalRectangleClicked.value = it
                    }
                }
                else{
                    displayDialog(clicked = externalRectangleClicked.value, text = (greetingText.value).toString(), dialogColor = Color(android.graphics.Color.parseColor("#818148")), uniqueMessage = "The embedded content has been marked as unknown"){
                        externalRectangleClicked.value = it
                    }
                }
            }

        }
    }

    //Function to display a dialog box to the user for if the user clicks on a section of the rectangle
    @Composable
    fun displayDialog(clicked: Boolean, text: String,dialogColor: Color, uniqueMessage: String, onDismiss: (Boolean) -> Unit) {
        var mutableClicked by remember { mutableStateOf(clicked) }
        val coroutineScope = rememberCoroutineScope()
        if (mutableClicked) {
            AnimatedTransitionDialog(
                onDismissRequest = {
                    coroutineScope.launch {
                        delay(300) // delay equal to the duration of the closing animation
                        mutableClicked = false
                    }
                },
                contentAlignment = Alignment.Center,
                content = { dialogHelper ->
                    Surface(
                        shape = RoundedCornerShape(16.dp),
                        color = dialogColor
                    ) {
                        Box(
                            modifier = Modifier
                                .padding(8.dp)
                                .background(dialogColor)
                                .wrapContentSize()
                        ) {
                            Column(
                                modifier = Modifier
                                    .padding(8.dp)
                            ) {
                                Text(text = "Scoring Prediction",
                                    style = MaterialTheme.typography.h4,
                                    modifier = Modifier.padding(20.dp),
                                    color = Color.White,
                                    textAlign = TextAlign.Center

                                )
                                Spacer(modifier = Modifier.height(10.dp))

                                Text(
                                    text = text,
                                    style = MaterialTheme.typography.h5,
                                    modifier = Modifier
                                        .padding(20.dp)
                                        .fillMaxWidth(),
                                    textAlign = TextAlign.Center
                                )

                                Text(
                                    text = "Scoring works on a rough scale of:",
                                    style = MaterialTheme.typography.body1,
                                    modifier = Modifier.padding(20.dp)
                                )

                                Text(
                                    text = "MORE negative = Benign",
                                    style = MaterialTheme.typography.body1,
                                    modifier = Modifier.padding(20.dp)
                                )
                                Text(
                                    text = "0 = Unknown",
                                    style = MaterialTheme.typography.body1,
                                    modifier = Modifier.padding(20.dp)
                                )
                                Text(
                                    text = "MORE positive = Malicious",
                                    style = MaterialTheme.typography.body1,
                                    modifier = Modifier.padding(20.dp)
                                )
                                Text(
                                    text = uniqueMessage,
                                    style = MaterialTheme.typography.body1,
                                    modifier = Modifier.padding(20.dp)
                                )
                            }
                            IconButton(
                                onClick = {
                                    dialogHelper.triggerAnimatedDismiss()
                                    coroutineScope.launch {
                                        delay(300) // delay equal to the duration of the closing animation
                                        mutableClicked = false
                                    }
                                },
                                modifier = Modifier
                                    .align(Alignment.TopEnd)
                                    .padding(8.dp)
                            ) {
                                Icon(Icons.Default.Close, contentDescription = "Close")
                            }
                        }
                    }
                }
            )
        }
        LaunchedEffect(mutableClicked) {
            if (!mutableClicked) {
                delay(300) // delay equal to the duration of the closing animation
                onDismiss(mutableClicked)
            }
        }
    }

    //Function to change the colour of the line between each rectangle
    private fun drawGradientLine(
        canvas: DrawScope,
        sectionWidth: Float,
        startColor: Color,
        endColor: Color,
        size: Size,
        animatedLength: Float
    ) {
        val path = androidx.compose.ui.graphics.Path().apply {
            moveTo(sectionWidth, size.height)
            lineTo(sectionWidth, size.height + animatedLength)
        }
        val brush = Brush.linearGradient(
            colors = listOf(startColor, endColor, endColor),
            start = Offset(sectionWidth, size.height),
            end = Offset(sectionWidth, size.height + animatedLength)
        )

        canvas.drawPath(
            path = path,
            brush = brush,
            style = Stroke(width = 10f)
        )
    }

    //Function to create the unique message to display to a user depending on the outcome of the analysis
    private fun drawRectangleSection(
        canvas: DrawScope,
        size: Size,
        endColor: Color,
        rectLeft: Float,
        rectRight: Float,
        message: String,
        scale: Float
    ) {
        canvas.scale(scale)
        {
            canvas.drawIntoCanvas { canvas ->
                val paint = Paint().apply {
                    color = endColor.toArgb()
                    style = android.graphics.Paint.Style.FILL
                }

                val rect = RectF(rectLeft, (size.height * 1.5).toFloat(), rectRight, size.height * 3)

                val path = Path().apply {
                    addRoundRect(
                        rect,
                        floatArrayOf(
                            50f, 50f,
                            50f, 50f,
                            50f, 50f,
                            50f, 50f
                        ),
                        android.graphics.Path.Direction.CW
                    )
                }
                canvas.nativeCanvas.drawPath(path, paint)

                val textPaint = Paint().apply {
                    color = Color(android.graphics.Color.parseColor("#FFFFFF")).toArgb()
                    textSize = 50f
                }

                var textWidth = calculateTextWidth(message, textPaint)

                // Reduce the text size until it fits the rectangle
                while (textWidth > rect.width()) {
                    textPaint.textSize = textPaint.textSize * 0.9f
                    textWidth = calculateTextWidth(message, textPaint)
                }

                // Draw the text
                canvas.nativeCanvas.drawText(message, size.height/ 3, (size.height * 2.5).toFloat(), textPaint)
            }
        }

    }

    fun calculateTextWidth(text: String, paint: Paint): Float {
        return paint.measureText(text)
    }

    //Function to load the tflite model and run the prediction
    @Composable
    fun GetTfliteModel() {
        val bundle = intent.extras
        var s:String? = null
        s = bundle!!.getString("barcode")

        embeddedURL.value = s.toString()

        val isLoading = remember { mutableStateOf(true) }

        //Load the tflite model
        val context = LocalContext.current
        val tflite = remember { mutableStateOf<Interpreter?>(null) }

        LaunchedEffect(Unit) {
            isLoading.value = true  // Show the progress bar

            // Run the coroutine for the tflite model
            launch {
                try {
                    val interpreter = Interpreter(loadModelFile())
                    tflite.value = interpreter

                    val featureVector = withContext(Dispatchers.Default) {
                        loadPythonData(s.toString(), progressValue,rates)
                    }

                    //print the values in the rates array
                    println("rates: ${rates.value?.toList()}")

                    updateText.value = "Formatting feature vector"

                    //convert the first element to an appropriate format for the tflite model
                    val featureVectorList = featureVector.let { it as List<*> }.map { it.toString().toFloat() }

                    val featureVectorBuffer = ByteBuffer.allocateDirect(4 * featureVectorList.size)
                    featureVectorBuffer.order(ByteOrder.nativeOrder())
                    featureVectorList.forEach { featureVectorBuffer.putFloat(it) }

                    println("featureVectorList: $featureVectorList")

                    val output = Array(1) { FloatArray(1) }
                    tflite.value?.run(featureVectorBuffer, output)

                    tflite.value?.close()

                    println(output[0].toList())

                    var cleanOutput = output[0].toList()

                    //print out the first element of the output
                    println("Output: ${cleanOutput[0]}")

                    progressValue.value = 1.0f

                    //Clear the text value from the screen
                    updateText.value = ""

                    // Update greeting text based on the output
                    greetingText.value = cleanOutput[0].toString()

                } catch (e: Exception) {
                    e.printStackTrace()
                } finally {
                    isLoading.value = false
                }
            }

            launch(Dispatchers.Main) {
                isLoading.value = false
            }

        }
    }

    //Function for overall graphics and UI for user interaction within the app.
    //Diplays the circular indicator for different features and processes the text which is displayed within
    @Composable
    private fun ProgressBarRootView(
        progress: Float,
        update: String,
        embeddedURL: String?,
        greetingText: String,
        rates: Array<*>?,
        outputMessage: Int?,
        fixedURL: String?
    ) {

        //Variables for knowing what is clicked
        var clickedSection by remember { mutableStateOf<Int?>(null) }

        var redSectionClicked by remember { mutableStateOf(false) }
        var blueSectionClicked by remember { mutableStateOf(false) }
        var greenSectionClicked by remember { mutableStateOf(false) }
        var pinkSectionClicked by remember { mutableStateOf(false) }
        var malBoxFlag by remember { mutableStateOf(false) }

        val currentProgress by animateFloatAsState(
            targetValue = progress,
            animationSpec = ProgressIndicatorDefaults.ProgressAnimationSpec
        )

        // Animate the stroke width and color
        val strokeWidth by animateDpAsState(
            targetValue = if (currentProgress < 1.0) 15.dp else 30.dp
        )
        val color by animateColorAsState(
            targetValue = if (currentProgress < 1.0) MaterialTheme.colors.secondary else Color.Red
        )



        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = update,
                modifier = Modifier.padding(10.dp),
                style = MaterialTheme.typography.h5
            )

            Box(
                modifier = Modifier
                    .size(300.dp)
                    .padding(10.dp)
            ) {
                //Check what to display progress bar wise. Both the loading and colour section output.
                if (currentProgress < 1.0) {
                    // Circular progress bar
                    CircularProgressIndicator(
                        progress = currentProgress,
                        modifier = Modifier.fillMaxSize(),
                        strokeWidth = strokeWidth,
                        color = color
                    )

                    // Display percentage in the center
                    Text(
                        text = "${(currentProgress * 100).toInt()}%",
                        modifier = Modifier.align(Alignment.Center),
                        style = MaterialTheme.typography.h6
                    )
                } else {

                    //Get the rate value messages for display
                    val (redTextDisplay,redTextMessage,redColourDisplay) = analyzeUrlFeatures(rates)
                    val (blueTextDisplay,blueTextMessage,blueColourDisplay) = analyzeJavaScriptFeatures(rates)
                    val (greenTextDisplay,greenTextMessage,greenColourDisplay) = analyzeHTMLFeatures(rates)
                    val (pinkTextDisplay,pinkTextMessage,pinkColourDisplay) = analyzeOtherFeatures(rates)

                    //Define the percent line variables for animation
                    var drawPercentProgress by remember { mutableStateOf(0f) }

                    //Create a launched effect to animate the lines
                    LaunchedEffect(key1 = true) {
                        while (drawPercentProgress < 1f) {
                            delay(20L)
                            drawPercentProgress += 0.02f
                        }
                    }

                    // Morph into a ring with clickable, colored sections
                    Canvas(modifier = Modifier
                        .fillMaxSize()
                        .pointerInput(Unit) {
                            // Detect taps on the canvas for each section adapted from: https://github.com/SmartToolFactory/Jetpack-Compose-Tutorials/blob/master/Tutorial1-1Basics/src/main/java/com/smarttoolfactory/tutorial1_1basics/chapter6_graphics/chart/PieChart.kt
                            detectTapGestures { offset ->
                                val centerX = size.width / 2
                                val centerY = size.height / 2
                                val dx = offset.x - centerX
                                val dy = offset.y - centerY
                                val distance = sqrt(dx * dx + dy * dy)
                                val radius = size.width / 2
                                val innerRadius = radius - strokeWidth.toPx()

                                if (distance >= innerRadius) {
                                    val angle =
                                        Math.toDegrees(Math.atan2(dy.toDouble(), dx.toDouble()))

                                    // Determine section clicked based off the angle of the click
                                    val section = when {
                                        angle < 0 -> (angle + 360) / 90
                                        else -> angle / 90
                                    }

                                    when (section.toInt()) {
                                        //Pink section (Other)
                                        0 -> pinkSectionClicked = true

                                        //Blue section (JavaScript)
                                        1 -> blueSectionClicked = true

                                        //Red section (URL)
                                        2 -> redSectionClicked = true

                                        //Green section (HTML)
                                        3 -> greenSectionClicked = true
                                    }

                                    clickedSection = section.toInt()

                                }
                            }
                        }) {

                        //Define the order of colours
                        val colors = listOf(
                            Color.Magenta,
                            Color.Blue,
                            Color.Red,
                            Color.Green
                        )

                        val totalArcAngle = 360f
                        val individualArcAngle = totalArcAngle / colors.size

                        //Draw the arc to display the text within the circle sections
                        for ((index, color) in colors.withIndex()) {
                            val startAngle = index * individualArcAngle
                            val sweepAngle = individualArcAngle

                            drawArc(
                                color = if (index == clickedSection) color.copy(alpha = 0.5f) else color,
                                startAngle = startAngle,
                                sweepAngle = sweepAngle,
                                useCenter = false,
                                style = Stroke(width = strokeWidth.toPx())
                            )

                            val textToDisplay = when (index) {
                                0 -> "Other" //
                                1 -> "Functionality" // JavaScript
                                2 -> "Website Link" //URL
                                3 -> "Website Content" //HTML
                                else -> ""
                            }

                            //Get the size of the canvas for mathematically placing elements on the screen
                            val path = Path()
                            val radius = size.width / 2 - 10.dp.toPx()
                            val centerX = size.width / 2
                            val centerY = size.height / 2

                            path.addArc(
                                RectF(centerX - radius, centerY - radius, centerX + radius, centerY + radius),
                                startAngle,
                                sweepAngle
                            )

                            drawIntoCanvas { canvas ->
                                val textPaint = Paint().apply {
                                    textAlign = Paint.Align.CENTER
                                    textSize = 20.sp.toPx()
                                }

                                canvas.nativeCanvas.drawTextOnPath(textToDisplay, path, 0f, 0f, textPaint)
                            }

                        }
                    }

                    //Check what symbol to display in the middle of the circle
                    val isNegative = greetingText.startsWith("-")

                    var lineProgress by remember { mutableStateOf(0f) }

                    //Create a launched effect to animate the lines
                    LaunchedEffect(key1 = true) {
                        while (lineProgress < 1f) {
                            delay(20L)  // delay for 20 milliseconds
                            lineProgress += 0.02f
                        }
                    }

                    val animatedProgress by animateFloatAsState(
                        targetValue = lineProgress,
                        animationSpec = tween(durationMillis = 500, easing = LinearEasing)
                    )

                    if(isNegative)
                    {
                        //Output message is used as identifier for if the request was successful or not
                        if(outputMessage == 1 || outputMessage == 2)
                        {
                            //Display the yellow unknown bar

                            Canvas(modifier = Modifier.fillMaxSize()) {
                                val strokeWidth = 30.dp.toPx()
                                val centerX = size.width / 2
                                val centerY = size.height / 2
                                val radius = size.width / 2 - strokeWidth / 2

                                val start = Offset(centerX - radius / 2, centerY)
                                val end = Offset(centerX + radius / 2, centerY)

                                val currentEnd = start + (end - start) * animatedProgress

                                drawLine(
                                    color = Color(0x80, 0x80, 0x00),
                                    start = start,
                                    end = currentEnd,
                                    strokeWidth = strokeWidth / 4
                                )



                            }
                            CircularProgressIndicator(
                                progress = lineProgress,
                                modifier = Modifier
                                    .fillMaxSize()
                                    .scale(0.75f),
                                strokeWidth = 15.dp,
                                color = Color(0x80, 0x80, 0x00)
                            )


                        }
                        else
                        {
                            // Morph into a tick
                            Canvas(modifier = Modifier.fillMaxSize()) {
                                val strokeWidth = 30.dp.toPx()
                                val centerX = size.width / 2
                                val centerY = size.height / 2
                                val radius = size.width / 2 - strokeWidth / 2

                                val start_first_line = Offset(centerX - radius / 2, centerY)
                                val end_first_line = Offset(centerX - radius / 10, centerY + radius / 2)

                                val currentEnd_first_line = start_first_line + (end_first_line - start_first_line) * animatedProgress

                                drawLine(
                                    color = Color.Green,
                                    start = start_first_line,
                                    end = currentEnd_first_line,
                                    strokeWidth = strokeWidth / 4
                                )

                                val start_second_line = Offset(centerX - radius / 8, centerY + radius / 2)
                                val end_second_line = Offset(centerX + radius / 2, centerY - radius / 2)

                                val currentEnd_second_line = start_second_line + (end_second_line - start_second_line) * animatedProgress

                                drawLine(
                                    color = Color.Green,
                                    start = start_second_line,
                                    end = currentEnd_second_line,
                                    strokeWidth = strokeWidth / 4
                                )
                            }
                            CircularProgressIndicator(
                                progress = lineProgress,
                                modifier = Modifier
                                    .fillMaxSize()
                                    .scale(0.75f),
                                strokeWidth = 15.dp,
                                color = Color.Green
                            )


                        }


                    }
                    else{
                        //Output message is used as identifier for if the request was successful or not. Only 2 here as if negative it will be 1 or 2 by default
                        if(outputMessage == 2)
                        {
                            //Display the yellow unknown bar

                            Canvas(modifier = Modifier.fillMaxSize()) {
                                val strokeWidth = 30.dp.toPx()
                                val centerX = size.width / 2
                                val centerY = size.height / 2
                                val radius = size.width / 2 - strokeWidth / 2

                                val start = Offset(centerX - radius / 2, centerY)
                                val end = Offset(centerX + radius / 2, centerY)

                                val currentEnd = start + (end - start) * animatedProgress

                                drawLine(
                                    color = Color(0x80, 0x80, 0x00),
                                    start = start,
                                    end = currentEnd,
                                    strokeWidth = strokeWidth / 4
                                )

                            }
                            CircularProgressIndicator(
                                progress = lineProgress,
                                modifier = Modifier
                                    .fillMaxSize()
                                    .scale(0.75f),
                                strokeWidth = 15.dp,
                                color = Color(0x80, 0x80, 0x00)
                            )

                        }
                        else
                        {
                            // Morph into a red cross
                            Canvas(modifier = Modifier.fillMaxSize()) {
                                val strokeWidth = 30.dp.toPx()
                                val centerX = size.width / 2
                                val centerY = size.height / 2
                                val radius = size.width / 2 - strokeWidth / 2

                                val start_first_line = Offset(centerX - radius / 2, centerY - radius / 2)
                                val end_first_line = Offset(centerX + radius / 2, centerY + radius / 2)

                                var currentEnd_first_line = start_first_line + (end_first_line - start_first_line) * animatedProgress

                                drawLine(
                                    color = Color.Red,
                                    start = start_first_line,
                                    end = currentEnd_first_line,
                                    strokeWidth = strokeWidth / 4
                                )

                                val start_second_line = Offset(centerX + radius / 2, centerY - radius / 2)
                                val end_second_line = Offset(centerX - radius / 2, centerY + radius / 2)

                                var currentEnd_second_line = start_second_line + (end_second_line - start_second_line) * animatedProgress

                                drawLine(
                                    color = Color.Red,
                                    start = start_second_line,
                                    end = currentEnd_second_line,
                                    strokeWidth = strokeWidth / 4
                                )
                            }
                            CircularProgressIndicator(
                                progress = lineProgress,
                                modifier = Modifier
                                    .fillMaxSize()
                                    .scale(0.75f),
                                strokeWidth = 15.dp,
                                color = Color.Red
                            )
                        }

                    }

                    //Display the URL and buttons for accessing content related to the embedded content
                    if (embeddedURL != null) {
                        val shortenedURL = if (embeddedURL.length > 25) {
                            "${embeddedURL.take(22)}..."
                        } else {
                            embeddedURL
                        }


                        Column(
                            modifier = Modifier.align(Alignment.Center),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = shortenedURL,
                                style = MaterialTheme.typography.h6,
                                fontSize = 15.sp
                            )

                            val context = LocalContext.current
                            val intent = remember { Intent(Intent.ACTION_VIEW, Uri.parse(fixedURL)) }

                            //check if the output message is 0, if so display the button to open the URL in the browser
                            if(outputMessage == 0)
                            {
                                //check if neagtive is active, if so display the button to open the URL in the browser
                                if(isNegative)
                                {
                                    Button(
                                        onClick = {
                                            // Handle the button click
                                            println("Accessing browser page of URL: $fixedURL")
                                            context.startActivity(intent)

                                        },
                                        modifier = Modifier
                                            .padding(8.dp)
                                            .border(
                                                2.dp,
                                                Color(0x7B, 0x1F, 0xA2),
                                                MaterialTheme.shapes.medium
                                            )
                                            .background(Color.Transparent),
                                        colors = ButtonDefaults.buttonColors(backgroundColor = Color.Transparent)
                                    ) {
                                        Text("Open in Browser")
                                    }
                                }
                                //else display a button which opens a popup window to warn the user that they may be entering a malicious site
                                else
                                {
                                    Button(
                                        onClick = {
                                            //set the flag to true to display the dialog box
                                            malBoxFlag = true
                                        },
                                        modifier = Modifier
                                            .padding(8.dp)
                                            .border(
                                                2.dp,
                                                Color(0x7B, 0x1F, 0xA2),
                                                MaterialTheme.shapes.medium
                                            )
                                            .background(Color.Transparent),
                                        colors = ButtonDefaults.buttonColors(backgroundColor = Color.Transparent)
                                    ) {
                                        Text("Open in Browser")
                                    }
                                }

                            }

                        }
                    }

                    //Dialog box to display if the user clicks the button to open the URL in the browser but the URL is marked as malicious
                    if(malBoxFlag)
                    {
                        val context = LocalContext.current
                        val intent = remember { Intent(Intent.ACTION_VIEW, Uri.parse(fixedURL)) }

                        AnimatedTransitionDialog(
                            onDismissRequest = { malBoxFlag = false },
                            contentAlignment = Alignment.Center,
                            content = { dialogHelper ->
                                Surface(
                                    shape = RoundedCornerShape(16.dp),
                                    color = Color.Red
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .padding(8.dp)
                                            .background(Color.Red)
                                            .wrapContentSize()
                                    ) {
                                        Column(
                                            modifier = Modifier
                                                .padding(8.dp)
                                        ) {
                                            Text(
                                                text = "Warning",
                                                style = MaterialTheme.typography.h4,
                                                modifier = Modifier.padding(20.dp),
                                                color = Color.White,
                                                textAlign = TextAlign.Center
                                            )
                                            Spacer(modifier = Modifier.height(10.dp))

                                            Text(
                                                text = "The URL has been marked as malicious. Do you wish to proceed with visiting the website?",
                                                style = MaterialTheme.typography.body1,
                                                modifier = Modifier.padding(40.dp),
                                                color = Color.White
                                            )
                                            Row(
                                                horizontalArrangement = Arrangement.SpaceEvenly,
                                                modifier = Modifier.fillMaxWidth()
                                            ) {
                                                // Button for yes to proceed to website
                                                Button(
                                                    onClick = { context.startActivity(intent) },
                                                    colors = ButtonDefaults.buttonColors(backgroundColor = Color(android.graphics.Color.parseColor("#9c3107")))
                                                ) {
                                                    Text("Yes")
                                                }
                                                // Button for no to not proceed to website
                                                Button(
                                                    onClick = { dialogHelper.triggerAnimatedDismiss() },
                                                    colors = ButtonDefaults.buttonColors(backgroundColor = Color(android.graphics.Color.parseColor("#9c3107")))
                                                ) {
                                                    Text("No")
                                                }
                                            }
                                        }

                                        // Close Button
                                        IconButton(
                                            onClick = { dialogHelper.triggerAnimatedDismiss() },
                                            modifier = Modifier
                                                .align(Alignment.TopEnd)
                                                .padding(8.dp)
                                        ) {
                                            Icon(Icons.Default.Close, contentDescription = "Close")
                                        }
                                    }
                                }
                            }
                        )

                    }

                    //Dialog box functions to display depending on user input
                    if(redSectionClicked)
                    {

                        ColoredSectionDialog(
                            color = Color(android.graphics.Color.parseColor("#C64626")),
                            images = listOf(R.drawable.urllength, R.drawable.urldigits, R.drawable.comsymbol, R.drawable.ipsymbol, R.drawable.tldsymbol, R.drawable.urlsymbols, R.drawable.portsymbol, R.drawable.absoluterelative, R.drawable.fileext, R.drawable.urlobf),
                            text = redTextDisplay,
                            message = redTextMessage,
                            display = redColourDisplay,
                            secondColour = Color(android.graphics.Color.parseColor("#FF704D"))
                        ) { redSectionClicked = false;clickedSection = null}

                    }


                    if(greenSectionClicked)
                    {
                        ColoredSectionDialog(
                            color = Color(android.graphics.Color.parseColor("#70DB70")),
                            images = listOf(R.drawable.urllength, R.drawable.tagsymbols, R.drawable.emptyhyperlink, R.drawable.externalinternal, R.drawable.formsymbol, R.drawable.tagsymbols, R.drawable.copyrightsymbol, R.drawable.domainsymbol,R.drawable.iframesymbol,R.drawable.mailtosymbol),
                            text = greenTextDisplay,
                            message = greenTextMessage,
                            display = greenColourDisplay,
                            secondColour = Color(android.graphics.Color.parseColor("#7FF47F"))
                        ) { greenSectionClicked = false;clickedSection = null}
                    }

                    if(blueSectionClicked)
                    {
                        ColoredSectionDialog(
                            color = Color(android.graphics.Color.parseColor("#80D4FF")),
                            images = listOf(R.drawable.urllength, R.drawable.javapopup,R.drawable.javanative,R.drawable.javadom,R.drawable.javaobf),
                            text = blueTextDisplay,
                            message = blueTextMessage,
                            display = blueColourDisplay,
                            secondColour = Color(android.graphics.Color.parseColor("#A4DDFB"))
                        ) { blueSectionClicked = false;clickedSection = null}

                    }

                    if (pinkSectionClicked) {

                        ColoredSectionDialog(
                            color = Color(android.graphics.Color.parseColor("#FF80FF")),
                            images = listOf(R.drawable.redirectsymbol, R.drawable.whoissymbol, R.drawable.whoissymbol,R.drawable.whoissymbol,R.drawable.whoissymbol),
                            text = pinkTextDisplay,
                            message = pinkTextMessage,
                            display = pinkColourDisplay,
                            secondColour = Color(android.graphics.Color.parseColor("#FEA2FE"))
                        ) { pinkSectionClicked = false;clickedSection = null }
                    }

                }
            }
        }
    }

    //Function to display the information about certain features of the embedded content.
    @OptIn(ExperimentalPagerApi::class)
    @Composable
    fun ColoredSectionDialog(
        color: Color,
        images: List<Int>,
        text: List<String>,
        message: List<String>,
        display: List<Boolean>,
        secondColour: Color,
        onDismiss: () -> Unit
    ) {
        val pagerState = rememberPagerState(initialPage = 0)

        AnimatedTransitionDialog(
            onDismissRequest = onDismiss,
            contentAlignment = Alignment.Center,
            content = { dialogHelper ->
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (display[pagerState.currentPage]) secondColour else color
                ) {

                    //Create the unique text lists to display on each page
                    val statText = mutableListOf<String>()
                    val supportText = mutableListOf<String>()

                    if(!text.indices.isEmpty())
                    {
                        for (i in text.indices) {
                            statText.add(text[i])
                            supportText.add(message[i])
                        }
                    }

                    //Display the dialog box with the information about the embedded content
                    Box{
                        HorizontalPager(state = pagerState, count = images.size) { page ->
                            Column(modifier = Modifier
                                .padding(10.dp)
                                .wrapContentSize()) {
                                Image(
                                    painter = painterResource(id = images[page]),
                                    contentDescription = "Image for page $page",
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .aspectRatio(1f)
                                        .wrapContentSize()
                                )
                                Spacer(modifier = Modifier.height(20.dp))
                                Text(
                                    text = statText[page],
                                    modifier = Modifier.padding(10.dp),
                                    style = MaterialTheme.typography.h5,
                                    color = Color.White
                                )
                                Spacer(modifier = Modifier.height(10.dp))
                                Box(modifier = Modifier
                                    .clip(RoundedCornerShape(16.dp))
                                    .background(Color(android.graphics.Color.parseColor("#000000")))
                                    .padding(10.dp)
                                )
                                {
                                    Text(
                                        text = supportText[page],
                                        modifier = Modifier.padding(10.dp),
                                        style = MaterialTheme.typography.h5,
                                        color = Color.White
                                    )
                                }

                            }
                        }

                        //Display dots on the bottom of the dialog box to show the user which page they are on.
                        //Code adapted from: https://developer.android.com/jetpack/compose/layouts/pager
                        Row(
                            Modifier
                                .wrapContentHeight()
                                .fillMaxWidth()
                                .align(Alignment.BottomCenter)
                                .padding(bottom = 8.dp),
                            horizontalArrangement = Arrangement.Center
                        ) {
                            repeat(pagerState.pageCount) { iteration ->
                                val colorHold = if (pagerState.currentPage == iteration) Color(android.graphics.Color.parseColor("#FFFFFF")) else Color(android.graphics.Color.parseColor("#666666"))
                                Box(
                                    modifier = Modifier
                                        .padding(2.dp)
                                        .clip(CircleShape)
                                        .background(colorHold)
                                        .size(8.dp)
                                )
                            }
                        }

                        // Close Button
                        IconButton(
                            onClick = { dialogHelper.triggerAnimatedDismiss() },
                            modifier = Modifier
                                .align(Alignment.TopEnd)
                                .padding(8.dp)
                        ) {
                            Icon(Icons.Default.Close, contentDescription = "Close")
                        }

                    }

                }
            }
        )
    }



    //Function to display the text inside the dialog boxes of specific website features
    private fun analyzeUrlFeatures(rates: Array<*>?): Triple<MutableList<String>, MutableList<String>,MutableList<Boolean>> {
        val redTextDisplay = mutableListOf<String>()
        val redTextMessage = mutableListOf<String>()
        val redColourDisplay = mutableListOf<Boolean>()

        val totalLength = (rates?.get(16)?.toString()?.toFloat()?.plus(rates[17].toString().toFloat()) ?: 0f) + (rates?.get(18)?.toString()?.toFloat() ?: 0f)

        //print the length of the url
        redTextDisplay.add("The length of the URL was $totalLength characters long.")

        redTextMessage.add("A longer URL of 55 or more characters is considered more suspicious on average")

        if(totalLength >= 55)
        {
            redColourDisplay.add(true)
        }
        else
        {
            redColourDisplay.add(false)
        }

        val lengthDigits = (rates?.get(19)?.toString()?.toFloat()?.plus(rates[20].toString().toFloat()) ?: 0f) + (rates?.get(21)?.toString()?.toFloat() ?: 0f) //(rates?.get(19)?.toString()?.toInt() ?: 0) + rates?.get(20).toString().toInt() + rates?.get(21).toString().toInt()

        //Get the number of digits in the URL
        redTextDisplay.add("The URL contained $lengthDigits digits.")

        redTextMessage.add("3 or more digits in the URL is considered more suspicious on average")

        if(lengthDigits > 3)
        {
            redColourDisplay.add(true)
        }
        else
        {
            redColourDisplay.add(false)
        }

        //Check for .com subdomain
        if(rates?.get(13).toString() == "1.0")
        {
            redTextDisplay.add("URL contains .com subdomain")
            redColourDisplay.add(false)
        }
        else
        {
            redTextDisplay.add("URL does not contain .com subdomain")
            redColourDisplay.add(true)

        }

        redTextMessage.add("No .com subdomain is considered more suspicious.")

        //Check for IP address in URL
        if(rates?.get(14).toString() == "1.0")
        {
            redTextDisplay.add("URL contains IP address")
            redColourDisplay.add(true)
        }
        else
        {
            redTextDisplay.add("URL does not contain an IP address")
            redColourDisplay.add(false)
        }

        redTextMessage.add("An IP address is considered more suspicious")

        //Check for common TLD
        if(rates?.get(15).toString() == "1.0")
        {
            redTextDisplay.add("URL contains a common TLD")
            redColourDisplay.add(false)
        }
        else
        {
            redTextDisplay.add("URL does not contain a common TLD")
            redColourDisplay.add(true)
        }

        redTextMessage.add("No common TLD is considered more suspicious")

        //check if the symbol rates 22 - 30 are not empty excluding dot and slash
        if(rates?.get(22).toString() != "0.0" ||  rates?.get(25).toString() != "0.0" || rates?.get(26).toString() != "0.0" || rates?.get(27).toString() != "0.0" || rates?.get(28).toString() != "0.0" || rates?.get(29).toString() != "0.0" || rates?.get(30).toString() != "0.0" || rates?.get(41).toString() != "0.0" || rates?.get(42).toString() != "0.0")
        {

            var holdString = "URL contains unique symbols: "
            //redTextDisplay.add("URL contains unique symbols: ")

            //check the unique symbols
            if(rates?.get(22).toString() != "0.0")
            {
                holdString += " -,"
            }
            if(rates?.get(25).toString() != "0.0")
            {
                holdString += " @,"
            }
            if(rates?.get(26).toString() != "0.0")
            {
                holdString += " ?,"
            }
            if(rates?.get(27).toString() != "0.0")
            {
                holdString += " =,"
            }
            if(rates?.get(28).toString() != "0.0")
            {
                holdString += " _,"
            }
            if(rates?.get(29).toString() != "0.0")
            {
                holdString += " &,"
            }
            if(rates?.get(30).toString() != "0.0")
            {
                holdString += " ~,"
            }
            if(rates?.get(41).toString() != "0.0")
            {
                holdString += " %,"
            }
            if(rates?.get(42).toString() != "0.0")
            {
                holdString += " :,"
            }
            //remove the last comma from the string
            holdString = holdString.dropLast(1)
            redTextDisplay.add(holdString)
            redColourDisplay.add(true)
        }
        else{
            redTextDisplay.add("URL does not contain any unique symbols")
            redColourDisplay.add(false)
        }

        redTextMessage.add("More unique symbols is considered more suspicious")

        //check for port in url
        if(rates?.get(40).toString() != "0.0")
        {
            redTextDisplay.add("URL contains port")
            redColourDisplay.add(true)
        }
        else
        {
            redTextDisplay.add("URL does not contain a port")
            redColourDisplay.add(false)
        }

        redTextMessage.add("Containing a port is considered more suspicious")

        //Check if URL is relative or absolute
        if(rates?.get(43).toString() != "0.0")
        {
            redTextDisplay.add("URL is absolute")
            redColourDisplay.add(false)
        }
        else
        {
            redTextDisplay.add("URL is relative")
            redColourDisplay.add(true)

        }
        redTextMessage.add("Containing a relative URL is considered more suspicious")

        //check for an file extension in the url

        if(rates?.get(48).toString() != "0.0")
        {
            redTextDisplay.add("URL contains file extension")
            redColourDisplay.add(true)
        }
        else
        {
            redTextDisplay.add("URL does not contain a file extension")
            redColourDisplay.add(false)
        }

        redTextMessage.add("Containing a file extension is considered more suspicious")

        //Check for URL deobfuscation

        if(rates?.get(53).toString() != "0.0")
        {
            redTextDisplay.add("URL contains deobfuscation")
            redColourDisplay.add(true)
        }
        else
        {
            redTextDisplay.add("URL does not contain deobfuscation")
            redColourDisplay.add(false)
        }

        redTextMessage.add("Containing deobfuscation is considered more suspicious")


        redTextDisplay.add("DON'T DELETE ME")
        redTextMessage.add("DON'T DELETE ME")
        redColourDisplay.add(true)

        return Triple(redTextDisplay,redTextMessage,redColourDisplay)
    }

    private fun analyzeHTMLFeatures(rates: Array<*>?): Triple<MutableList<String>, MutableList<String>,MutableList<Boolean>> {
        //Array to store text to display to the user after all checks are complete
        val greenTextDisplay = mutableListOf<String>()
        val greenTextMessage = mutableListOf<String>()
        val greenColourDisplay = mutableListOf<Boolean>()


        //Display the body length
        greenTextDisplay.add("The length of the HTML body was ${rates?.get(31)?.toString()} characters long.")

        greenTextMessage.add("A HTML body length less than 1000 is considered more suspicious on average")

        if(rates?.get(31)?.toString()?.toFloat()!! < 1000)
        {
            greenColourDisplay.add(true)
        }
        else
        {
            greenColourDisplay.add(false)
        }

        //Display the number of tags on the page
        greenTextDisplay.add("There were ${rates[6]?.toString()} tags found on the page.")

        greenTextMessage.add("50 or less tags is considered more suspicious on average")

        if(rates[6]?.toString()?.toFloat()!! < 50)
        {
            greenColourDisplay.add(true)
        }
        else
        {
            greenColourDisplay.add(false)
        }

        //Get the number of empty hyperlinks
        if(rates[5]?.toString() != "0")
        {
            greenTextDisplay.add("There were ${rates[5]?.toString()} empty hyperlinks found.")
            greenColourDisplay.add(true)
        }
        else
        {
            greenTextDisplay.add("There were no empty hyperlinks found.")
            greenColourDisplay.add(false)
        }

        greenTextMessage.add("A higher number of empty hyperlinks is considered more suspicious")

        //Check for if there are more internal to external hyperlinks or vice versa
        if(rates[7].toString() > rates[8].toString())
        {
            greenTextDisplay.add("More internal hyperlinks than external hyperlinks were found")
            greenColourDisplay.add(false)
        }
        else if(rates[7].toString() < rates[8].toString())
        {
            greenTextDisplay.add("More external hyperlinks than internal hyperlinks were found")
            greenColourDisplay.add(true)
        }
        else
        {
            greenTextDisplay.add("Equal number of internal and external hyperlinks found")
            greenColourDisplay.add(false)
        }

        greenTextMessage.add("Less hyperlinks is considered more suspicious")


        //Check if there are more than 0 suspicious forms
        if(rates[12].toString() != "0.0")
        {
            greenTextDisplay.add("Potential suspicious forms flagged within website")
               greenColourDisplay.add(true)

        }
        else
        {
            greenTextDisplay.add("No suspicious forms found within website")
            greenColourDisplay.add(false)
        }

        greenTextMessage.add("The greater number of flagged forms is considered more suspicious")

        //Check if there are more paired tags than single tags
        if(rates[32].toString() > rates[33].toString())
        {
            greenTextDisplay.add("More paired tags than single tags")
            greenColourDisplay.add(false)
        }
        else if(rates[32].toString() < rates[33].toString())
        {
            greenTextDisplay.add("More single tags than paired tags")
            greenColourDisplay.add(true)
        }
        else
        {
            greenTextDisplay.add("Equal number of paired and single tags")
        }

        greenTextMessage.add("More single tags within the website is considered more suspicious")

        //Check if there is copyright within the html
        if(rates[34].toString() == "1.0")
        {
            greenTextDisplay.add("HTML contains © symbol")
            greenColourDisplay.add(false)
        }
        else
        {
            greenTextDisplay.add("HTML does not contain © symbol")
            greenColourDisplay.add(true)
        }

        greenTextMessage.add("No © symbol is considered more suspicious. It is a common symbol for copyright purposes.")

        //check if the domain is in the html
        if(rates[35].toString() == "1.0")
        {
            greenTextDisplay.add("Domain can be found in the HTML")
            greenColourDisplay.add(false)
        }
        else
        {
            greenTextDisplay.add("Domain cannot be found in the HTML")
            greenColourDisplay.add(true)
        }

        greenTextMessage.add("The domain name of the site not being found in the HTML is considered more suspicious")

        //Check for iframe tags
        if(rates[37].toString() != "0.0")
        {
            greenTextDisplay.add("iframe tags found in the HTML.")
            greenColourDisplay.add(true)
        }
        else
        {
            greenTextDisplay.add("No iframe tags found in the HTML.")
            greenColourDisplay.add(false)
        }

        greenTextMessage.add("The presence of iframe tags is considered more suspicious as it can be used to embed malicious content.")

        //Check for mailto tags
        if(rates[38].toString() != "0.0")
        {
            greenTextDisplay.add("mailto tags found in the HTML.")
            greenColourDisplay.add(true)
        }
        else
        {
            greenTextDisplay.add("No mailto tags found in the HTML.")
            greenColourDisplay.add(false)
        }

        greenTextMessage.add("The presence of mailto tags is considered more suspicious")

        greenTextDisplay.add("DON'T DELETE ME")
        greenTextMessage.add("DONT DELETE ME")
        greenColourDisplay.add(true)

        return Triple(greenTextDisplay, greenTextMessage,greenColourDisplay)

    }

    private fun analyzeJavaScriptFeatures(rates: Array<*>?): Triple<MutableList<String>, MutableList<String>,MutableList<Boolean>> {
        val blueTextDisplay = mutableListOf<String>()
        val blueTextMessage = mutableListOf<String>()
        val blueColourDisplay = mutableListOf<Boolean>()

        //Get the length of the JavaScript content
        blueTextDisplay.add("The length of the JavaScript content was ${rates?.get(52)?.toString()} characters long.")
        blueTextMessage.add("A longer JavaScript content is considered more suspicious")

        if(rates?.get(52)?.toString()?.toFloat()!! > 35000)
        {
            blueColourDisplay.add(true)
        }
        else
        {
            blueColourDisplay.add(false)
        }

        //Check for javascript popup
        if(rates[39].toString() != "0.0")
        {
            blueTextDisplay.add("JavaScript contains popup")
            blueColourDisplay.add(true)
        }
        else
        {
            blueTextDisplay.add("JavaScript does not contain popup")
            blueColourDisplay.add(false)
        }

        blueTextMessage.add("The presence of a popup is considered more suspicious due to the potential for malicious content within.")

        //Check for native functions
        if(rates[49].toString() != "0.0")
        {
            blueTextDisplay.add("JavaScript contains native functions")
            blueColourDisplay.add(true)
        }
        else
        {
            blueTextDisplay.add("JavaScript does not contain native functions")
            blueColourDisplay.add(false)
        }

        blueTextMessage.add("The presence of native functions is considered more suspicious as they can be exploited on the website.")

        //Check for javascript DOM structure elements
        if(rates[50].toString() != "0.0")
        {
            blueTextDisplay.add("JavaScript contains DOM structure elements")
            blueColourDisplay.add(true)
        }
        else
        {
            blueTextDisplay.add("JavaScript does not contain DOM structure elements")
            blueColourDisplay.add(false)
        }

        blueTextMessage.add("The presence of DOM structure elements is considered more suspicious as they are functions that can be used to manipulate the HTML content.")

        //Check for javascript obfuscation
        if(rates[51].toString() != "0.0")
        {
            blueTextDisplay.add("JavaScript contains obfuscation")
            blueColourDisplay.add(true)
        }
        else
        {
            blueTextDisplay.add("JavaScript does not contain obfuscation")
            blueColourDisplay.add(false)
        }

        blueTextMessage.add("The presence of obfuscation is considered more suspicious as it can be used to hide malicious content.")

        blueTextDisplay.add("DON'T DELETE ME")
        blueTextMessage.add("DONT DELETE ME")
        blueColourDisplay.add(true)

        return Triple(blueTextDisplay,blueTextMessage,blueColourDisplay)
    }

    private fun analyzeOtherFeatures(rates: Array<*>?): Triple<MutableList<String>, MutableList<String>,MutableList<Boolean>> {
        val pinkTextDisplay = mutableListOf<String>()
        val pinkTextMessage = mutableListOf<String>()
        val pinkColourDisplay = mutableListOf<Boolean>()


        //Get the number of redirects
        pinkTextDisplay.add("The number of redirects was ${rates?.get(36)?.toString()}")
        pinkTextMessage.add("A higher number of redirects is considered more suspicious")

        if(rates?.get(36)?.toString()?.toFloat()?.toInt()!! > 5)
        {
            pinkColourDisplay.add(true)
        }
        else
        {
            pinkColourDisplay.add(false)
        }

        //Check the whois creation date
        pinkTextDisplay.add("The domain was created on ${rates[44]?.toString()}")
        pinkTextMessage.add("A more recent domain creation date is considered more suspicious")

        pinkColourDisplay.add(false)

        //Check the whois expiration date
        pinkTextDisplay.add("The domain will expire on ${rates[45]?.toString()}")
        pinkTextMessage.add("A sooner domain expiration date is considered more suspicious")
        pinkColourDisplay.add(false)

        //check the whois update date
        pinkTextDisplay.add("The domain was last updated on ${rates[46]?.toString()}")
        pinkTextMessage.add("A more recent domain update date is considered more suspicious")
        pinkColourDisplay.add(false)

        //Check for the presence of a registrar
        if(rates[47].toString() != "0.0")
        {
            pinkTextDisplay.add("The domain contains a registrar")
            pinkColourDisplay.add(false)
        }
        else
        {
            pinkTextDisplay.add("The domain does not contain a registrar")
            pinkColourDisplay.add(true)
        }
        pinkTextMessage.add("The lack of a registrar is considered more suspicious")

        pinkTextDisplay.add("DON'T DELETE ME")
        pinkTextMessage.add("DONT DELETE ME")
        pinkColourDisplay.add(true)

        return Triple(pinkTextDisplay,pinkTextMessage,pinkColourDisplay)
    }


    //Function to load and extract the data from the URL using the python file
    private fun loadPythonData(toString: String, progressValue: MutableState<Float>, rateValues: MutableState<Array<*>?>): List<Any>? {

        //Initialize python runtime
        val python = Python.getInstance()
        val pythonFile = python.getModule("chaqFeatureExtract")

        updateText.value = "Reformatting URL"

        //Get the old url
        val oldUrlFunction: PyObject? = pythonFile.get("get_old_url")
        val oldUrl: PyObject? = oldUrlFunction?.call(toString)
        println("Old URL: $oldUrl")

        //Fix the url format for making request
        val fixUrlFormatFunction: PyObject? = pythonFile.get("fix_url_format")
        val fixedUrlExtract: PyObject? = fixUrlFormatFunction?.call(toString)
        val fixedUrlFeatures = fixedUrlExtract?.asList()

        //Get the value from the fixed url
        val fixedUrl = fixedUrlFeatures?.getOrNull(0)?.toString()
        holdFixedURL.value = fixedUrl
        val missing_scheme = fixedUrlFeatures?.getOrNull(1)?.toInt()

        println("Fixed URL: $fixedUrl")
        println("Missing Scheme: $missing_scheme")

        progressValue.value = 0.1f


        /*
            Get the extracted features from the html content

            Broken down into more granular functions to provide more detailed loading screen

            Functions include 4 main extractions with multiple sub extractions

            Rate values are used as the number identifiers for the extractions.

            URL:

                -	1
                -	16 – 18
                -	19 – 33
                -   43 - 46
                -   51
                -   56

            HTML:

                -   2
                -	3 – 15
                -	34 – 38
                -   40 - 41


            JavaScript:

                -   42
                -   52 - 55


            Other:

                -  39
                -  47 - 50

        */


        updateText.value = "Making request to URL"

        //Get the html content from the URL
        val htmlContentFunction: PyObject? = pythonFile.get("get_html_content")
        val htmlContentExtract: PyObject? = htmlContentFunction?.call(fixedUrl,missing_scheme)
        val htmlContentFeatures = htmlContentExtract?.asList()

        val htmlContent = htmlContentFeatures?.getOrNull(0)?.toString()
        val outputMessage = htmlContentFeatures?.getOrNull(1)?.toInt()
        val rate39 = htmlContentFeatures?.getOrNull(2)?.toFloat()
        val rate47 = htmlContentFeatures?.getOrNull(3)?.toFloat()
        val rate48 = htmlContentFeatures?.getOrNull(4)?.toFloat()
        val rate49 = htmlContentFeatures?.getOrNull(5)?.toFloat()
        val rate50 = htmlContentFeatures?.getOrNull(6)?.toFloat()

        println("output message: $outputMessage")

        holdOutputMessage.value = outputMessage

        progressValue.value = 0.3f

        //Get the URL features

        updateText.value = "Collecting URL sequence"

        //Get the URL sequence feature
        val urlSequenceFunction: PyObject? = pythonFile.get("url_sequence")
        val urlSequence: PyObject? = urlSequenceFunction?.call(fixedUrl)
        println("URL Sequence: $urlSequence")

        progressValue.value = 0.4f

        updateText.value = "Collecting domain features"

        //Get the URL feature quantities
        val domainFeatureFunction: PyObject? = pythonFile.get("domain_features")
        val domainFeatureExtract: PyObject? = domainFeatureFunction?.call(fixedUrl,fixedUrl)
        val splitDomainFeatures = domainFeatureExtract?.asList()



        val rate16 = splitDomainFeatures?.getOrNull(0)?.toFloat()
        println("rate16: $rate16")
        val rate17 = splitDomainFeatures?.getOrNull(1)?.toFloat()
        println("rate17: $rate17")
        val rate18 = splitDomainFeatures?.getOrNull(2)?.toFloat()
        println("rate18: $rate18")


        //Get the domain digit quantities

        updateText.value = "Collecting domain digit features"

        val domainDigitFunction: PyObject? = pythonFile.get("domain_digit_features")
        val domainDigitExtract: PyObject? = domainDigitFunction?.call(fixedUrl,fixedUrl)
        val splitDomainDigitFeatures = domainDigitExtract?.asList()


        val rate19 = splitDomainDigitFeatures?.getOrNull(0)?.toFloat()
        val rate20 = splitDomainDigitFeatures?.getOrNull(1)?.toFloat()
        val rate21 = splitDomainDigitFeatures?.getOrNull(2)?.toFloat()
        val rate22 = splitDomainDigitFeatures?.getOrNull(3)?.toFloat()
        val rate23 = splitDomainDigitFeatures?.getOrNull(4)?.toFloat()
        val rate24 = splitDomainDigitFeatures?.getOrNull(5)?.toFloat()
        val rate25 = splitDomainDigitFeatures?.getOrNull(6)?.toFloat()
        val rate26 = splitDomainDigitFeatures?.getOrNull(7)?.toFloat()
        val rate27 = splitDomainDigitFeatures?.getOrNull(8)?.toFloat()
        val rate28 = splitDomainDigitFeatures?.getOrNull(9)?.toFloat()
        val rate29 = splitDomainDigitFeatures?.getOrNull(10)?.toFloat()
        val rate30 = splitDomainDigitFeatures?.getOrNull(11)?.toFloat()
        val rate31 = splitDomainDigitFeatures?.getOrNull(12)?.toFloat()
        val rate32 = splitDomainDigitFeatures?.getOrNull(13)?.toFloat()
        val rate33 = splitDomainDigitFeatures?.getOrNull(14)?.toFloat()
        val rate43 = splitDomainDigitFeatures?.getOrNull(15)?.toFloat()
        val rate44 = splitDomainDigitFeatures?.getOrNull(16)?.toFloat()
        val rate45 = splitDomainDigitFeatures?.getOrNull(17)?.toFloat()
        val rate46 = splitDomainDigitFeatures?.getOrNull(18)?.toFloat()
        val rate51 = splitDomainDigitFeatures?.getOrNull(19)?.toFloat()
        val rate56 = splitDomainDigitFeatures?.getOrNull(20)?.toFloat()



        //Get the HTML features

        //Get the HTML tag quantities

        updateText.value = "Collecting HTML tag features"

        val htmlTagFunction: PyObject? = pythonFile.get("html_tag_features")
        val htmlTagExtract: PyObject? = htmlTagFunction?.call(htmlContent)
        val splitHtmlTagFeatures = htmlTagExtract?.asList()



        val rate3 = splitHtmlTagFeatures?.getOrNull(0)?.toFloat()
        val rate4 = splitHtmlTagFeatures?.getOrNull(1)?.toFloat()
        val rate5 = splitHtmlTagFeatures?.getOrNull(2)?.toFloat()
        val rate6 = splitHtmlTagFeatures?.getOrNull(3)?.toFloat()
        val rate7 = splitHtmlTagFeatures?.getOrNull(4)?.toFloat()
        val rate8 = splitHtmlTagFeatures?.getOrNull(5)?.toFloat()
        val rate9 = splitHtmlTagFeatures?.getOrNull(6)?.toFloat()

        progressValue.value = 0.5f

        //Get the hyperlink quantities

        updateText.value = "Collecting hyperlink features"

        val hyperlinkFunction: PyObject? = pythonFile.get("hyperlink_features")
        val hyperlinkExtract: PyObject? = hyperlinkFunction?.call(htmlContent,fixedUrl)
        val splitHyperlinkFeatures = hyperlinkExtract?.asList()


        val rate10 = splitHyperlinkFeatures?.getOrNull(0)?.toFloat()
        val rate11 = splitHyperlinkFeatures?.getOrNull(1)?.toFloat()
        val rate12 = splitHyperlinkFeatures?.getOrNull(2)?.toFloat()
        val rate13 = splitHyperlinkFeatures?.getOrNull(3)?.toFloat()

        progressValue.value = 0.6f

        updateText.value = "Collecting form features"

        //Get the form quantities
        val formFunction: PyObject? = pythonFile.get("form_features")
        val formExtract: PyObject? = formFunction?.call(htmlContent)
        val splitFormFeatures = formExtract?.asList()

        val rate14 = splitFormFeatures?.getOrNull(0)?.toFloat()
        val rate15 = splitFormFeatures?.getOrNull(1)?.toFloat()

        progressValue.value = 0.7f

        updateText.value = "Collecting body features"

        //Get the body/copyright quantities
        val bodyFunction: PyObject? = pythonFile.get("body_features")
        val bodyExtract: PyObject? = bodyFunction?.call(htmlContent,fixedUrl)
        val splitBodyFeatures = bodyExtract?.asList()


        val rate34 = splitBodyFeatures?.getOrNull(0)?.toFloat()
        val rate35 = splitBodyFeatures?.getOrNull(1)?.toFloat()
        val rate36 = splitBodyFeatures?.getOrNull(2)?.toFloat()
        val rate37 = splitBodyFeatures?.getOrNull(3)?.toFloat()
        val rate38 = splitBodyFeatures?.getOrNull(4)?.toFloat()
        val rate40 = splitBodyFeatures?.getOrNull(5)?.toFloat()
        val rate41 = splitBodyFeatures?.getOrNull(6)?.toFloat()

        progressValue.value = 0.8f

        //Get the JavaScript features

        updateText.value = "Collecting JavaScript features"

        //Get the JavaScript tag quantities
        val javaScriptFunction: PyObject? = pythonFile.get("get_javascript_features")
        val javaScriptExtract: PyObject? = javaScriptFunction?.call(htmlContent)
        val splitJavaScriptFeatures = javaScriptExtract?.asList()

        progressValue.value = 0.9f

        val rate42 = splitJavaScriptFeatures?.getOrNull(0)?.toFloat()
        val rate52 = splitJavaScriptFeatures?.getOrNull(1)?.toFloat()
        val rate53 = splitJavaScriptFeatures?.getOrNull(2)?.toFloat()
        val rate54 = splitJavaScriptFeatures?.getOrNull(3)?.toFloat()
        val rate55 = splitJavaScriptFeatures?.getOrNull(4)?.toFloat()


        updateText.value = "Creating feature vector"



        //Check if the request was successful and or the embedded code is not a url
        if (outputMessage == 2) {
            // If it is, create a feature vector of 5254 zeros
            val featureVector = List(5254) { 0f }
            rateValues.value = arrayOf(rate3,rate4,rate5,rate6,rate7,rate8,rate9,rate10,rate11,rate12,rate13,rate14,rate15,rate16,rate17,rate18,rate19,rate20,rate21,rate22,rate23,rate24,rate25,rate26,rate27,rate28,rate29,rate30,rate31,rate32,rate33,rate34,rate35,rate36,rate37,rate38,rate39,rate40,rate41,rate42,rate43,rate44,rate45,rate46,rate47,rate48,rate49,rate50,rate51,rate52,rate53,rate54,rate55,rate56)
            return featureVector
        } else {
            // Otherwise, proceed with the existing code to produce the feature vector
            val featureVectorFunction: PyObject? = pythonFile.get("createFeatureVector")
            val featureExtract: PyObject? = featureVectorFunction?.call(urlSequence,htmlContent)
            println("Feature vector android: $featureExtract")

            val pyList = featureExtract?.asList()
            val featureVector: List<PyObject>? = pyList?.map{it}

            //Get the length of the feature vector
            val featureVectorLength = featureVector?.size
            println("featureVectorLength: $featureVectorLength")

            println("Feature vector: $featureVector")

            println("conversion finished")

            rateValues.value = arrayOf(rate3,rate4,rate5,rate6,rate7,rate8,rate9,rate10,rate11,rate12,rate13,rate14,rate15,rate16,rate17,rate18,rate19,rate20,rate21,rate22,rate23,rate24,rate25,rate26,rate27,rate28,rate29,rate30,rate31,rate32,rate33,rate34,rate35,rate36,rate37,rate38,rate39,rate40,rate41,rate42,rate43,rate44,rate45,rate46,rate47,rate48,rate49,rate50,rate51,rate52,rate53,rate54,rate55,rate56)

            return featureVector
        }

    }


    //Functions to display the animated dialog box. Animated code adapted from: https://medium.com/bilue/expanding-dialog-in-jetpack-compose-a6be40deab86
    @OptIn(ExperimentalAnimationApi::class)
    @Composable
    internal fun AnimatedScaleInTransition(
        visible: Boolean,
        content: @Composable AnimatedVisibilityScope.() -> Unit
    ) {
        AnimatedVisibility(
            visible = visible,
            enter = scaleIn(
                animationSpec = tween(500)
            ),
            exit = scaleOut(
                animationSpec = tween(500)
            ),
            content = content
        )
    }


    suspend fun startDismissWithExitAnimation(
        animateTrigger: MutableState<Boolean>,
        onDismissRequest: () -> Unit
    ) {
        animateTrigger.value = false
        delay(600)
        onDismissRequest()
    }


    class AnimatedTransitionDialogHelper(
        private val coroutineScope: CoroutineScope,
        private val onDismissFlow: MutableSharedFlow<Any>) {

        fun triggerAnimatedDismiss() {
            coroutineScope.launch {
                onDismissFlow.emit(Any())
            }
        }
    }

    @Composable
    fun AnimatedTransitionDialog(
        onDismissRequest: () -> Unit,
        contentAlignment: Alignment = Alignment.Center,
        content: @Composable (AnimatedTransitionDialogHelper) -> Unit
    ) {
        val onDismissSharedFlow: MutableSharedFlow<Any> = remember { MutableSharedFlow() }
        val coroutineScope: CoroutineScope = rememberCoroutineScope()
        val animateTrigger = remember { mutableStateOf(false) }

        LaunchedEffect(key1 = Unit) {
            launch {
                delay(250)
                animateTrigger.value = true
            }
            launch {
                onDismissSharedFlow.asSharedFlow().collectLatest {
                    startDismissWithExitAnimation(animateTrigger, onDismissRequest)
                }
            }
        }

        Dialog(
            onDismissRequest = {
                coroutineScope.launch {
                    startDismissWithExitAnimation(animateTrigger, onDismissRequest)
                }
            }
        ) {
            Box(contentAlignment = contentAlignment,
                modifier = Modifier.fillMaxSize()
            ) {
                AnimatedScaleInTransition(visible = animateTrigger.value) {
                    content(AnimatedTransitionDialogHelper(coroutineScope, onDismissSharedFlow))
                }
            }
        }
    }



    //Function to load the tflite model from the assets folder
    private fun loadModelFile(): MappedByteBuffer {
        val fileDescriptor: AssetFileDescriptor = assets.openFd("modelv9_float16.tflite")
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel: FileChannel = inputStream.channel
        val startOffset: Long = fileDescriptor.startOffset
        val declaredLength: Long = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

}

//Function to convert the python list to a kotlin list
private fun PyObject?.toArray(): Any {
    return this?.asList()?.map { it.toString().toFloat() } ?: emptyList<Float>()

}






//Basic functions to display the app
@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    EmbedAnalyseTheme {
        Greeting("Android")
    }
}

@Composable
fun MyApp(displayText: String) {
    Surface(
        modifier = Modifier.fillMaxSize()
    ) {
        // Use the Text composable to display the text
        Text(
            text = displayText,
            modifier = Modifier.padding(16.dp),
            style = MaterialTheme.typography.body1
        )
    }
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    FeatureReaderTheme {
        MyApp("Example text to preview")
    }
}

@Composable
fun FeatureReaderTheme(content: @Composable () -> Unit) {
    TODO("Not yet implemented")
}

