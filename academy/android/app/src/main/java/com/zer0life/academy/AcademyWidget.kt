package com.zer0life.academy
import android.content.Context
import androidx.glance.*
import androidx.glance.appwidget.*
import androidx.glance.appwidget.action.actionStartActivity
import androidx.glance.action.clickable
import androidx.glance.layout.*
import androidx.glance.text.*
import androidx.compose.ui.unit.dp
class AcademyWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            Column(GlanceModifier.fillMaxSize().padding(16.dp).clickable(actionStartActivity<MainActivity>())) {
                Text("ZER0LIFE")
                Text("Open Academy")
                Text("Continue learning")
            }
        }
    }
}
class AcademyReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget = AcademyWidget()
}
