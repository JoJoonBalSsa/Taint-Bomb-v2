package io.JoJoonBalSsa.TaintBomb.settings

import com.intellij.openapi.components.*
import com.intellij.util.xmlb.XmlSerializerUtil

@State(
    name = "TaintBombSettings",
    storages = [Storage("taintBombSettings.xml")]
)
@Service
class TaintBombSettings : PersistentStateComponent<TaintBombSettings> {
    var enableRemoveComments: Boolean = true
    var enableStringObfuscate: Boolean = true
    var enableLevelObfuscate: Boolean = true
    var enableIdentifierObfuscate: Boolean = true
    var enableMainAnalysis: Boolean = true

    companion object {
        fun getInstance(): TaintBombSettings {
            return service<TaintBombSettings>()
        }
    }

    override fun getState(): TaintBombSettings = this

    override fun loadState(state: TaintBombSettings) {
        XmlSerializerUtil.copyBean(state, this)
    }
}
