"""
Utilitários para Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StreamlitUtils:
    """Classe para utilitários do Streamlit"""
    
    @staticmethod
    def display_metrics(metrics: Dict[str, Any], columns: int = 4):
        """
        Exibir métricas em colunas
        
        Args:
            metrics: Dicionário com métricas
            columns: Número de colunas
        """
        try:
            cols = st.columns(columns)
            for i, (key, value) in enumerate(metrics.items()):
                with cols[i % columns]:
                    if isinstance(value, (int, float)):
                        st.metric(key, value)
                    else:
                        st.metric(key, str(value))
        except Exception as e:
            logger.error(f"Erro ao exibir métricas: {str(e)}")
    
    @staticmethod
    def display_dataframe(df: pd.DataFrame, title: str = "", 
                         max_rows: int = 1000, use_container_width: bool = True):
        """
        Exibir DataFrame com formatação
        
        Args:
            df: DataFrame para exibir
            title: Título da seção
            max_rows: Máximo de linhas para exibir
            use_container_width: Usar largura total do container
        """
        try:
            if title:
                st.subheader(title)
            
            if len(df) > max_rows:
                st.warning(f"Exibindo apenas as primeiras {max_rows} linhas de {len(df)}")
                df_display = df.head(max_rows)
            else:
                df_display = df
            
            st.dataframe(df_display, use_container_width=use_container_width)
            
        except Exception as e:
            logger.error(f"Erro ao exibir DataFrame: {str(e)}")
            st.error("Erro ao exibir dados")
    
    @staticmethod
    def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                        title: str = "", color_col: Optional[str] = None):
        """
        Criar gráfico de barras
        
        Args:
            df: DataFrame com dados
            x_col: Coluna para eixo X
            y_col: Coluna para eixo Y
            title: Título do gráfico
            color_col: Coluna para cores
        """
        try:
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de barras: {str(e)}")
            st.error("Erro ao criar gráfico")
    
    @staticmethod
    def create_pie_chart(df: pd.DataFrame, values_col: str, names_col: str, 
                        title: str = ""):
        """
        Criar gráfico de pizza
        
        Args:
            df: DataFrame com dados
            values_col: Coluna com valores
            names_col: Coluna com nomes
            title: Título do gráfico
        """
        try:
            fig = px.pie(df, values=values_col, names=names_col, title=title)
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de pizza: {str(e)}")
            st.error("Erro ao criar gráfico")
    
    @staticmethod
    def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                         title: str = "", color_col: Optional[str] = None):
        """
        Criar gráfico de linha
        
        Args:
            df: DataFrame com dados
            x_col: Coluna para eixo X
            y_col: Coluna para eixo Y
            title: Título do gráfico
            color_col: Coluna para cores
        """
        try:
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de linha: {str(e)}")
            st.error("Erro ao criar gráfico")
    
    @staticmethod
    def create_summary_card(title: str, value: Any, subtitle: str = "", 
                          icon: str = "📊"):
        """
        Criar card de resumo
        
        Args:
            title: Título do card
            value: Valor principal
            subtitle: Subtítulo
            icon: Ícone
        """
        try:
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid #1f77b4;
                margin: 1rem 0;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                    <h3 style="margin: 0; color: #1f77b4;">{title}</h3>
                </div>
                <div style="font-size: 2rem; font-weight: bold; color: #262730;">
                    {value}
                </div>
                {f'<div style="color: #666; font-size: 0.9rem;">{subtitle}</div>' if subtitle else ''}
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Erro ao criar card de resumo: {str(e)}")
            st.error("Erro ao criar card")
    
    @staticmethod
    def create_progress_section(title: str, steps: List[str], 
                              current_step: int = 0):
        """
        Criar seção de progresso
        
        Args:
            title: Título da seção
            steps: Lista de etapas
            current_step: Etapa atual
        """
        try:
            st.subheader(title)
            
            for i, step in enumerate(steps):
                if i < current_step:
                    st.success(f"✅ {step}")
                elif i == current_step:
                    st.info(f"🔄 {step}")
                else:
                    st.write(f"⏳ {step}")
            
        except Exception as e:
            logger.error(f"Erro ao criar seção de progresso: {str(e)}")
    
    @staticmethod
    def create_download_button(data: Any, filename: str, 
                             button_text: str = "📥 Download",
                             mime_type: str = "application/octet-stream"):
        """
        Criar botão de download
        
        Args:
            data: Dados para download
            filename: Nome do arquivo
            button_text: Texto do botão
            mime_type: Tipo MIME
        """
        try:
            st.download_button(
                label=button_text,
                data=data,
                file_name=filename,
                mime=mime_type
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar botão de download: {str(e)}")
            st.error("Erro ao criar botão de download")
    
    @staticmethod
    def create_expandable_section(title: str, content: str, 
                                expanded: bool = False):
        """
        Criar seção expansível
        
        Args:
            title: Título da seção
            content: Conteúdo
            expanded: Se deve estar expandida
        """
        try:
            with st.expander(title, expanded=expanded):
                st.markdown(content)
                
        except Exception as e:
            logger.error(f"Erro ao criar seção expansível: {str(e)}")
    
    @staticmethod
    def create_alert(message: str, alert_type: str = "info"):
        """
        Criar alerta
        
        Args:
            message: Mensagem
            alert_type: Tipo de alerta (info, success, warning, error)
        """
        try:
            if alert_type == "info":
                st.info(message)
            elif alert_type == "success":
                st.success(message)
            elif alert_type == "warning":
                st.warning(message)
            elif alert_type == "error":
                st.error(message)
            else:
                st.write(message)
                
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {str(e)}")
    
    @staticmethod
    def create_sidebar_section(title: str, content: Any):
        """
        Criar seção na sidebar
        
        Args:
            title: Título da seção
            content: Conteúdo
        """
        try:
            with st.sidebar:
                st.header(title)
                if isinstance(content, str):
                    st.markdown(content)
                else:
                    st.write(content)
                    
        except Exception as e:
            logger.error(f"Erro ao criar seção na sidebar: {str(e)}")
    
    @staticmethod
    def create_tabs(tab_names: List[str]):
        """
        Criar abas
        
        Args:
            tab_names: Lista de nomes das abas
            
        Returns:
            Lista de containers das abas
        """
        try:
            return st.tabs(tab_names)
            
        except Exception as e:
            logger.error(f"Erro ao criar abas: {str(e)}")
            return [st.container() for _ in tab_names]
    
    @staticmethod
    def create_columns(num_columns: int):
        """
        Criar colunas
        
        Args:
            num_columns: Número de colunas
            
        Returns:
            Lista de containers das colunas
        """
        try:
            return st.columns(num_columns)
            
        except Exception as e:
            logger.error(f"Erro ao criar colunas: {str(e)}")
            return [st.container() for _ in range(num_columns)]
    
    @staticmethod
    def create_file_uploader(label: str, file_types: List[str], 
                           help_text: str = ""):
        """
        Criar uploader de arquivo
        
        Args:
            label: Label do uploader
            file_types: Tipos de arquivo aceitos
            help_text: Texto de ajuda
            
        Returns:
            Arquivo uploadado
        """
        try:
            return st.file_uploader(
                label=label,
                type=file_types,
                help=help_text
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar uploader: {str(e)}")
            return None
