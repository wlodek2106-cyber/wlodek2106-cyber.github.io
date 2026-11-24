package com.zer0life.academy
import android.content.Context
import android.content.Intent
import androidx.glance.*
import androidx.glance.appwidget.*
import androidx.glance.appwidget.action.actionStartActivity
import androidx.glance.action.clickable
import androidx.glance.layout.*
import androidx.glance.text.*
import androidx.compose.ui.unit.dp
class AcademyWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        val store = context.getSharedPreferences("academy_progress", Context.MODE_PRIVATE)
        val total = store.getInt("total",0)
        val completed = store.getInt("completed",0)
        val valid = total in listOf(30,40,45) && completed in 0..total
        provideContent {
            Column(GlanceModifier.fillMaxSize().padding(16.dp).clickable(actionStartActivity(Intent(context, MainActivity::class.java)))) {
                Text("ZER0LIFE")
                Text(if(valid) "${completed * 100 / total}% · $completed / $total" else "Open Academy")
                Text("Continue learning")
            }
        }
    }
}
class AcademyReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget = AcademyWidget()
}
