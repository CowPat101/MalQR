package com.example.malqrdetect

//import com.jetpack.barcodescanner.ui.theme.BarcodeScannerTheme
import BarCodeAnalyser
import android.Manifest
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.AnimatedVisibilityScope
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.animation.core.tween
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.layout.wrapContentSize
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.material.Icon
import androidx.compose.material.IconButton
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.core.content.ContextCompat
import com.chaquo.python.Python
import com.example.malqrdetect.ui.theme.BarcodeScannerTheme
import com.google.accompanist.pager.ExperimentalPagerApi
import com.google.accompanist.pager.HorizontalPager
import com.google.accompanist.pager.rememberPagerState
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberPermissionState
import com.google.common.util.concurrent.ListenableFuture
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

@ExperimentalPermissionsApi
class MainActivity : ComponentActivity() {
    //private var isIntentTriggered by mutableStateOf(false)
    private var isPythonInitialized by mutableStateOf(false)

    private var showDialog by  mutableStateOf(false)

    //var showTutorial by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            LaunchedEffect(true)
            {
                GlobalScope.launch {
                    //Code to start the python interpreter so it runs in the background to speed up the process
                    val python = Python.getInstance()
                    val pythonFile = python.getModule("chaqFeatureExtract")

                    // Mark Python as initialized
                    isPythonInitialized = true


                }
            }

            setContent{

                BarcodeScannerTheme {

                    Surface(color = MaterialTheme.colors.background) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Bottom
                        ) {

                            // Request Camera Permission from the user
                            val cameraPermissionState = rememberPermissionState(permission = Manifest.permission.CAMERA)


                            //Code to get the camera permission. Adapted from: https://medium.com/@rzmeneghelo/how-to-request-permissions-in-jetpack-compose-a-step-by-step-guide-7ce4b7782bd7
                            val requestPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()
                            ) { isGranted ->
                                if (isGranted) {
                                    println("Permission Granted!")
                                    showDialog = false

                                } else {
                                    println("Permission Denied!")
                                    //Display a dialog box to the user that the app needs the camera permission to work
                                    showDialog = true

                                }
                            }

                            //Camera permission state checks
                            LaunchedEffect(cameraPermissionState.hasPermission)
                            {
                                showDialog = !cameraPermissionState.hasPermission
                            }

                            //Give two attempts to request the camera permission otherwise manual request must occur
                            LaunchedEffect(cameraPermissionState) {
                                if (!cameraPermissionState.hasPermission && cameraPermissionState.shouldShowRationale) {
                                    requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                                } else {
                                    requestPermissionLauncher.launch(Manifest.permission.CAMERA)

                                }
                            }

                            if(showDialog)
                            {
                                CameraPermissionDialog()
                            }


                            CameraPreview()
                        }
                    }
                }
            }

        }
    }

    //Function to display the dialog box that the app needs the camera permission to work
    @Composable
    fun CameraPermissionDialog() {
        AnimatedTransitionDialog(
            onDismissRequest = {},
            contentAlignment = Alignment.Center,
            content = {
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = Color.Black
                ) {
                    Box(
                        modifier = Modifier
                            .padding(8.dp)
                            .background(Color.Black)
                            .wrapContentSize()
                    ) {
                        Column(
                            modifier = Modifier
                                .padding(8.dp)
                        ) {
                            Text(
                                text = "Camera Permission is required to use the app. Please grant the permission to continue.",
                                style = MaterialTheme.typography.body1,
                                modifier = Modifier.padding(40.dp),
                                color = Color.White
                            )
                            Text(
                                text ="Go to Settings > Permissions > Camera to grant the permission",
                                style = MaterialTheme.typography.body1,
                                modifier = Modifier.padding(40.dp),
                                color = Color.White
                            )

                            //Make a button to go to the settings to grant the permission to allow the camera to work
                            val context = LocalContext.current

                            Button(onClick = {
                                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                                val uri = Uri.fromParts("package", context.packageName, null)
                                intent.data = uri
                                context.startActivity(intent)
                            }, modifier = Modifier.align(Alignment.CenterHorizontally)) {
                                Text("Open Settings")
                            }
                        }
                    }
                }
            }
        )
    }

}






//Function for displaying the camera onscreen
@OptIn(ExperimentalPagerApi::class)
@Composable
fun CameraPreview() {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var preview by remember { mutableStateOf<Preview?>(null) }
    val barCodeVal = remember { mutableStateOf("") }
    val showTutorial = remember { mutableStateOf(true) }

    Box(modifier = Modifier.fillMaxSize()){
        //Make it so that if the tutorial is shown, the camera preview is not displayed
        if (showTutorial.value) {
            AndroidView(
                factory = { AndroidViewContext ->
                    // Configure PreviewView for camera preview
                    PreviewView(AndroidViewContext).apply {
                        this.scaleType = PreviewView.ScaleType.FILL_CENTER
                        layoutParams = ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            ViewGroup.LayoutParams.MATCH_PARENT,
                        )
                        implementationMode = PreviewView.ImplementationMode.COMPATIBLE
                    }
                },
                modifier = Modifier
                    .fillMaxSize(),

                update = { previewView ->
                    // Define the camera to use (Back), the executor and provider for the camera
                    val cameraSelector: CameraSelector = CameraSelector.Builder()
                        .requireLensFacing(CameraSelector.LENS_FACING_BACK)
                        .build()
                    val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
                    val cameraProviderFuture: ListenableFuture<ProcessCameraProvider> =
                        ProcessCameraProvider.getInstance(context)

                    cameraProviderFuture.addListener({
                        // Start the camera preview, barcode scanner and image analysis
                        preview = Preview.Builder().build().also {
                            it.setSurfaceProvider(previewView.surfaceProvider)
                        }
                        val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
                        val barcodeAnalyser = BarCodeAnalyser { barcodes ->
                            barcodes.forEach { barcode ->
                                barcode.rawValue?.let { barcodeValue ->
                                    if(showTutorial.value)
                                    {
                                        // Display the extracted value in a toast
                                        barCodeVal.value = barcodeValue
                                        Toast.makeText(context, barcodeValue, Toast.LENGTH_SHORT).show()
                                        // Send embedded content to Analyse activity
                                        val intent = Intent(context, EmbedAnalyse::class.java)
                                        intent.putExtra("barcode", barcodeValue)
                                        context.startActivity(intent)
                                    }

                                }
                            }
                        }
                        val imageAnalysis: ImageAnalysis = ImageAnalysis.Builder()
                            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                            .build()
                            .also {
                                it.setAnalyzer(cameraExecutor, barcodeAnalyser)
                            }

                        try {
                            // Unbind the camera if already in use and apply to the lifecycle
                            cameraProvider.unbindAll()
                            cameraProvider.bindToLifecycle(
                                lifecycleOwner,
                                cameraSelector,
                                preview,
                                imageAnalysis
                            )
                        } catch (e: Exception) {
                            Log.d("TAG", "CameraPreview: ${e.localizedMessage}")
                        }
                    }, ContextCompat.getMainExecutor(context))
                }
            )
        }

        Button(
            onClick = {showTutorial.value = false},
            modifier = Modifier.align(Alignment.TopCenter)
        ){
            Text("Tutorial")
        }

    }

    //Make a list of text to display on each page of the tutorial
    val text = listOf(
        "Scan a code and learn it's result!",
        "Analyse it's content",
        "View it's score",
        "Open the browser"
    )

    //Make a list of messages to display on each page of the tutorial
    val message = listOf(
        "Point the camera at a QR code to initiate the scan. The app will display the content of the QR code.",
        "Tap on a ring to learn more about the content of the QR code.",
        "View the score from the model to see if the content is malicious or not.",
        "Open the browser to view the content of the QR code."
    )

    //Make a list of images to display on each page of the tutorial
    val images = listOf(
        R.drawable.mainmenu,
        R.drawable.statmenu,
        R.drawable.predscore,
        R.drawable.openbrowser
    )

    if(!showTutorial.value){

        val pagerState = rememberPagerState(initialPage = 0)

        AnimatedTransitionDialog(
            onDismissRequest = {showTutorial.value = true },
            contentAlignment = Alignment.Center,
            content = { dialogHelper ->
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = Color.Black
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
                            Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
                        }

                    }

                }
            }
        )
    }



}



//Functions to display the animated dialog box. Animated code adapted from: https://medium.com/bilue/expanding-dialog-in-jetpack-compose-a6be40deab86
@OptIn(ExperimentalAnimationApi::class)
@Composable
fun AnimatedScaleInTransition(
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
    private val onDismissFlow: MutableSharedFlow<Any>
) {

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

