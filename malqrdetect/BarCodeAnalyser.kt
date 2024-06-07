
import android.annotation.SuppressLint
import android.util.Log
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import com.google.mlkit.vision.barcode.Barcode
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import java.util.concurrent.TimeUnit

@SuppressLint("UnsafeOptInUsageError")
class BarCodeAnalyser(private val onBarcodeDetected: (barcodes: List<Barcode>) -> Unit, ): ImageAnalysis.Analyzer {

    private var lastAnalyzedTimeStamp = 0L

    override fun analyze(image: ImageProxy) {

        val currentTimestamp = System.currentTimeMillis()

        //Analyse a frame taken once every second
        if (currentTimestamp - lastAnalyzedTimeStamp >= TimeUnit.SECONDS.toMillis(1)) {
            image.image?.let { imageToAnalyze ->

                //Configure the barcode scanner options
                val options = BarcodeScannerOptions.Builder()
                    .setBarcodeFormats(Barcode.FORMAT_ALL_FORMATS)
                    .build()
                //Create barcode scanner with options
                val barcodeScanner = BarcodeScanning.getClient(options)
                //Allow rotation of image within the scanning process / Convert image Proxy to an inputImage for processing
                val imageToProcess = InputImage.fromMediaImage(imageToAnalyze, image.imageInfo.rotationDegrees)


                //Process the image
                barcodeScanner.process(imageToProcess)
                    .addOnSuccessListener { barcodes ->
                        if (barcodes.isNotEmpty()) {
                            onBarcodeDetected(barcodes)
                        } else {
                            Log.d("TAG", "analyze: No barcode Scanned")
                        }
                    }
                    .addOnFailureListener { exception ->
                        Log.d("TAG", "BarcodeAnalyser: Something went wrong $exception")
                    }
                    .addOnCompleteListener {
                        image.close()
                    }
            }
            lastAnalyzedTimeStamp = currentTimestamp
        } else {
            //Close image proxy if 1 second has passed since last analysis
            image.close()
        }
    }
}
